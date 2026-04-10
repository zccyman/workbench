#!/usr/bin/env python3
"""
WeChat Database Decryption Tool

Extracts the database key from WeChat process memory and decrypts all databases.
Must be run on Windows with WeChat running (for key extraction).

Usage:
    python decrypt_wechat.py --extract-key                # Extract key from running WeChat
    python decrypt_wechat.py --decrypt-all                 # Decrypt all backed-up databases
    python decrypt_wechat.py --decrypt-all --key HEX_KEY   # Decrypt with specific key
    python decrypt_wechat.py --decrypt-all --input DIR     # Use custom input directory
"""

import os
import sys
import json
import argparse
import shutil
from pathlib import Path

DEFAULT_BACKUP_DIR = r"D:\backup\chat-records\wechat"
DEFAULT_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
    "data",
    "wechat_decrypted",
)
KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".wechat_key")


def extract_key():
    """Extract database key from WeChat process memory (Windows only)."""
    if sys.platform != "win32":
        print("ERROR: Key extraction only works on Windows.")
        print("Run this script in Windows PowerShell, not WSL.")
        sys.exit(1)

    try:
        import ctypes
        from ctypes import wintypes
    except ImportError:
        print("ERROR: ctypes not available.")
        sys.exit(1)

    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)

    PROCESSES_SNAPSHOT = 0x00000002
    TH32CS_SNAPPROCESS = 0x00000002
    MAX_PATH = 260

    class PROCESSENTRY32(ctypes.Structure):
        _fields_ = [
            ("dwSize", wintypes.DWORD),
            ("cntUsage", wintypes.DWORD),
            ("th32ProcessID", wintypes.DWORD),
            ("th32DefaultHeapID", ctypes.POINTER(ctypes.c_ulong)),
            ("th32ModuleID", wintypes.DWORD),
            ("cntThreads", wintypes.DWORD),
            ("th32ParentProcessID", wintypes.DWORD),
            ("pcPriClassBase", ctypes.c_long),
            ("dwFlags", wintypes.DWORD),
            ("szExeFile", ctypes.c_char * MAX_PATH),
        ]

    print("[*] Looking for WeChat process...")
    hSnapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    proc_entry = PROCESSENTRY32()
    proc_entry.dwSize = ctypes.sizeof(PROCESSENTRY32)

    wechat_pid = None
    if kernel32.Process32First(hSnapshot, ctypes.byref(proc_entry)):
        while True:
            exe_name = proc_entry.szExeFile.decode("utf-8", errors="ignore").lower()
            if exe_name in ("wechat.exe", "wechatstore.exe"):
                wechat_pid = proc_entry.th32ProcessID
                print(f"[+] Found WeChat process: PID {wechat_pid}")
                break
            if not kernel32.Process32Next(hSnapshot, ctypes.byref(proc_entry)):
                break

    kernel32.CloseHandle(hSnapshot)

    if not wechat_pid:
        print("[-] WeChat is not running. Please start WeChat first.")
        sys.exit(1)

    PROCESS_VM_READ = 0x0010
    PROCESS_QUERY_INFORMATION = 0x0400

    hProcess = kernel32.OpenProcess(
        PROCESS_VM_READ | PROCESS_QUERY_INFORMATION, False, wechat_pid
    )
    if not hProcess:
        print(f"[-] Failed to open WeChat process. Error: {kernel32.GetLastError()}")
        print("    Try running as Administrator.")
        sys.exit(1)

    print("[*] Searching for database key in process memory...")

    base_addr = 0x10000000
    end_addr = 0x7FFFFFFF
    chunk_size = 4096 * 1024

    key = None
    addr = base_addr
    while addr < end_addr:
        buf = (ctypes.c_char * chunk_size)()
        bytes_read = ctypes.c_size_t()

        if kernel32.ReadProcessMemory(
            hProcess, ctypes.c_void_p(addr), buf, chunk_size, ctypes.byref(bytes_read)
        ):
            data = buf.raw[: bytes_read.value]
            marker = b"-----BEGIN RSA PRIVATE KEY-----"
            idx = data.find(marker)
            if idx >= 0:
                potential_key_offset = idx + len(marker) + 78
                if potential_key_offset + 32 <= len(data):
                    candidate = data[potential_key_offset : potential_key_offset + 32]
                    if all(0x20 <= b < 0x7F for b in candidate):
                        key = candidate.hex()
                        print(f"[+] Found potential key: {key}")
                        break
        addr += chunk_size

    kernel32.CloseHandle(hProcess)

    if not key:
        print("[-] Could not find database key.")
        print("    This may happen if WeChat version is not supported.")
        print(
            "    Try: search for 'WeChatWin.dll' base address + known offset for your version."
        )
        sys.exit(1)

    with open(KEY_FILE, "w") as f:
        f.write(key)
    print(f"[+] Key saved to {KEY_FILE}")
    print(f"[+] You can now run: python {sys.argv[0]} --decrypt-all")
    return key


def load_key() -> str:
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            return f.read().strip()
    return ""


def decrypt_database(input_path: str, output_path: str, key: str):
    """Decrypt a single SQLCipher database to plain SQLite."""
    try:
        from pysqlcipher3 import dbapi2 as sqlcipher
    except ImportError:
        print("[-] pysqlcipher3 not installed. Run: pip install pysqlcipher3")
        sys.exit(1)

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    conn = sqlcipher.connect(input_path)
    conn.execute(f"PRAGMA key = \"x'{key}'\"")
    conn.execute("PRAGMA cipher_page_size = 4096")
    conn.execute("PRAGMA kdf_iter = 64000")

    try:
        conn.execute("SELECT count(*) FROM sqlite_master")
    except Exception as e:
        conn.close()
        raise Exception(f"Failed to decrypt {input_path}: {e}")

    plaintext_conn = sqlite3.connect(output_path)
    conn.backup(plaintext_conn)
    plaintext_conn.close()
    conn.close()


def decrypt_all(input_dir: str, output_dir: str, key: str):
    """Decrypt all databases in input_dir to output_dir."""
    import sqlite3

    os.makedirs(output_dir, exist_ok=True)
    count = 0
    failed = 0

    for root, dirs, files in os.walk(input_dir):
        for f in files:
            if f.endswith(("-shm", "-wal", "-journal")):
                continue
            if not f.endswith(".db"):
                continue

            src = os.path.join(root, f)
            rel = os.path.relpath(src, input_dir)
            dst = os.path.join(output_dir, rel)

            print(f"[*] Decrypting {rel}...", end=" ")
            try:
                decrypt_database(src, dst, key)
                count += 1
                print("OK")
            except Exception as e:
                failed += 1
                print(f"FAILED: {e}")

    print(f"\n[+] Decryption complete: {count} succeeded, {failed} failed")
    print(f"[+] Output: {output_dir}")


def main():
    parser = argparse.ArgumentParser(description="WeChat Database Decryption Tool")
    parser.add_argument(
        "--extract-key", action="store_true", help="Extract key from running WeChat"
    )
    parser.add_argument(
        "--decrypt-all", action="store_true", help="Decrypt all backed-up databases"
    )
    parser.add_argument("--key", type=str, help="Hex key (if not using saved key)")
    parser.add_argument(
        "--input", type=str, default=DEFAULT_BACKUP_DIR, help="Input backup directory"
    )
    parser.add_argument(
        "--output", type=str, default=DEFAULT_OUTPUT_DIR, help="Output directory"
    )

    args = parser.parse_args()

    if args.extract_key:
        extract_key()
    elif args.decrypt_all:
        key = args.key or load_key()
        if not key:
            print("[-] No key found. Run --extract-key first or provide --key.")
            sys.exit(1)
        decrypt_all(args.input, args.output, key)
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
