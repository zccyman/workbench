#!/usr/bin/env python3
"""
QQ NTQQ Database Decryption Tool

Extracts the database key from QQ process memory and decrypts all databases.
Must be run on Windows with QQ running (for key extraction).

Usage:
    python decrypt_qq.py --extract-key                # Extract key from running QQ
    python decrypt_qq.py --decrypt-all                 # Decrypt all backed-up databases
    python decrypt_qq.py --decrypt-all --key HEX_KEY   # Decrypt with specific key
    python decrypt_qq.py --decrypt-all --input DIR     # Use custom input directory
"""

import os
import sys
import json
import argparse
import shutil
from pathlib import Path

DEFAULT_BACKUP_DIR = r"D:\backup\chat-records\qq"
DEFAULT_OUTPUT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "qq_decrypted"
)
KEY_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".qq_key")


def extract_key():
    """Extract database key from QQ process memory (Windows only)."""
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

    print("[*] Looking for QQ process...")
    hSnapshot = kernel32.CreateToolhelp32Snapshot(TH32CS_SNAPPROCESS, 0)
    proc_entry = PROCESSENTRY32()
    proc_entry.dwSize = ctypes.sizeof(PROCESSENTRY32)

    qq_pid = None
    if kernel32.Process32First(hSnapshot, ctypes.byref(proc_entry)):
        while True:
            exe_name = proc_entry.szExeFile.decode("utf-8", errors="ignore").lower()
            if exe_name in ("qq.exe", "qqnt.exe"):
                qq_pid = proc_entry.th32ProcessID
                print(f"[+] Found QQ process: PID {qq_pid}")
                break
            if not kernel32.Process32Next(hSnapshot, ctypes.byref(proc_entry)):
                break

    kernel32.CloseHandle(hSnapshot)

    if not qq_pid:
        print("[-] QQ is not running. Please start QQ first.")
        sys.exit(1)

    print("[!] QQ NTQQ database decryption is experimental.")
    print("[!] The encryption method may vary by QQ version.")
    print()
    print("[*] Alternative approaches:")
    print("    1. Use LiteLoaderQQNT + db_dump plugin")
    print("    2. Use NapCatQQ framework to export chat history")
    print("    3. Export from QQ Message Manager (消息管理器) → Export as TXT")
    print()
    print("[*] For QQ Message Manager export:")
    print("    1. Open QQ → Settings → Message Management")
    print("    2. Select conversations to export")
    print("    3. Export as .txt or .mht")
    print("    4. Use the import function to parse exported files")
    sys.exit(0)


def load_key() -> str:
    if os.path.exists(KEY_FILE):
        with open(KEY_FILE, "r") as f:
            return f.read().strip()
    return ""


def decrypt_database(input_path: str, output_path: str, key: str):
    """Decrypt a single encrypted database to plain SQLite."""
    try:
        from pysqlcipher3 import dbapi2 as sqlcipher
    except ImportError:
        print("[-] pysqlcipher3 not installed. Run: pip install pysqlcipher3")
        sys.exit(1)

    import sqlite3

    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    conn = sqlcipher.connect(input_path)
    conn.execute(f"PRAGMA key = \"x'{key}'\"")

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
    os.makedirs(output_dir, exist_ok=True)
    count = 0
    failed = 0

    for root, dirs, files in os.walk(input_dir):
        for f in files:
            if f.endswith(
                ("-shm", "-wal", "-journal", "-first.material", "-last.material")
            ):
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
    parser = argparse.ArgumentParser(description="QQ NTQQ Database Decryption Tool")
    parser.add_argument(
        "--extract-key", action="store_true", help="Extract key from running QQ"
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
