# Workbench

A personal toolbox website — a collection of daily-use tools in one place.

## Features

- 🔧 **Auto-discovery**: Add a new tool by creating a directory — no config needed
- 🔒 **Authentication**: Login-protected personal tools
- 🌙 **Theme Support**: Light and dark modes
- 📱 **Responsive**: Works on desktop and mobile

## Tech Stack

- **Backend**: Python + FastAPI + SQLite
- **Frontend**: React + TypeScript + Vite + Tailwind CSS

## Getting Started

### Prerequisites

- Node.js 18+
- Python 3.8+

### Installation

```bash
# Backend
cd backend
pip install -r requirements.txt

# Frontend
cd frontend
npm install
```

### Run

```bash
./start.sh
```

Or manually:

```bash
# Backend (port 8001)
cd backend && uvicorn main:app --reload --port 8001

# Frontend (port 5173)
cd frontend && npm run dev
```

## Adding a New Tool

1. Create `backend/tools/<tool_id>/` directory
2. Add `router.py` with a FastAPI `APIRouter`
3. Add `meta.json` with tool metadata
4. Create frontend page `frontend/src/pages/tools/<ToolName>.tsx`
5. Restart the server — tool auto-registers!

### meta.json Example

```json
{
  "name": "My Tool",
  "id": "my_tool",
  "description": "A description of my tool",
  "icon": "🛠️",
  "category": "开发工具",
  "version": "1.0.0"
}
```

## Included Tools

| Tool | Description |
|------|-------------|
| WSL Path Bridge | Browse WSL filesystem and convert paths between WSL and Windows formats |

## License

MIT
