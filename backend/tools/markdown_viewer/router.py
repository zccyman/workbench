from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
import os
from pathlib import Path

router = APIRouter(tags=["markdown_viewer"])

def safe_path(p: str) -> str:
    resolved = os.path.realpath(p)
    allowed = ["/mnt", "/home", "/tmp", "/etc"]
    if not any(resolved.startswith(a) for a in allowed):
        raise HTTPException(403, f"路径不允许访问: {p}")
    return resolved

@router.get("/dir")
def list_dir(path: str = Query("/mnt")):
    try:
        sp = safe_path(path)
        if not os.path.isdir(sp):
            raise HTTPException(404, "目录不存在")
        entries = []
        for entry in sorted(os.scandir(sp), key=lambda e: (not e.is_dir(), e.name.lower())):
            if entry.is_dir():
                entries.append({"name": entry.name, "path": entry.path, "type": "directory"})
            elif entry.is_file() and entry.name.lower().endswith('.md'):
                stat = entry.stat()
                entries.append({
                    "name": entry.name, "path": entry.path, "type": "file",
                    "size": stat.st_size, "modified": stat.st_mtime,
                })
        return {"entries": entries, "path": sp}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/file")
def read_file(path: str = Query(...)):
    try:
        sp = safe_path(path)
        if not os.path.isfile(sp):
            raise HTTPException(404, "文件不存在")
        if not sp.lower().endswith('.md'):
            raise HTTPException(400, "只支持.md文件")
        for enc in ['utf-8', 'utf-8-sig', 'gbk', 'latin-1']:
            try:
                content = Path(sp).read_text(encoding=enc)
                stat = os.stat(sp)
                return {
                    "content": content, "path": sp, "size": stat.st_size,
                    "modified": stat.st_mtime, "encoding": enc,
                    "lines": content.count('\n') + 1,
                }
            except UnicodeDecodeError:
                continue
        raise HTTPException(500, "无法解码文件")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

class SaveRequest(BaseModel):
    path: str
    content: str

@router.put("/file")
def save_file(req: SaveRequest):
    try:
        sp = safe_path(req.path)
        if not os.path.isfile(sp):
            raise HTTPException(404, "文件不存在")
        backup = sp + ".bak"
        if os.path.exists(sp):
            import shutil
            shutil.copy2(sp, backup)
        Path(sp).write_text(req.content, encoding='utf-8')
        stat = os.stat(sp)
        return {"success": True, "path": sp, "size": stat.st_size, "lines": req.content.count('\n') + 1}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))

@router.get("/search")
def search_files(path: str = Query("/mnt"), keyword: str = Query(...)):
    try:
        sp = safe_path(path)
        results = []
        for root, dirs, files in os.walk(sp):
            for f in files:
                if not f.lower().endswith('.md'):
                    continue
                fp = os.path.join(root, f)
                try:
                    content = Path(fp).read_text(encoding='utf-8', errors='ignore')
                    if keyword.lower() in content.lower():
                        matches = []
                        for i, line in enumerate(content.split('\n'), 1):
                            if keyword.lower() in line.lower():
                                matches.append({"line": i, "text": line.strip()[:100]})
                                if len(matches) >= 3:
                                    break
                        results.append({"path": fp, "name": f, "matches": matches})
                        if len(results) >= 20:
                            return {"results": results, "truncated": True}
                except:
                    pass
        return {"results": results, "truncated": False}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(500, str(e))
