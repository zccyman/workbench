import sys
from pathlib import Path

# 将 backend 目录加入 Python 路径
backend_dir = Path(__file__).parent.parent / "backend"
sys.path.insert(0, str(backend_dir))
