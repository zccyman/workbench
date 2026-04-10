# Workbench - Personal Toolbox Website

Workbench is an open-source personal toolbox website built with FastAPI + React + TypeScript + Tailwind CSS + Vite.

## Features

- 🔐 **Authentication System** - Secure user registration and login
- 🛠️ **Tool Auto-discovery** - Automatically discovers and registers tools
- 📁 **WSL Path Bridge** - Browse WSL file system and convert paths between WSL and Windows
- 🎨 **Theme Support** - Light and dark theme support
- 📊 **Tool Management** - Centralized tool registry with metadata
- 🤖 **AI Session Manager** - Browse, search, and export Kilo Code / OpenCode AI coding sessions
- 💬 **Chat Records** - One-click backup, decrypt, import, and search for WeChat / QQ / Feishu chat history
- 📊 **Usage Monitor** - AI tool usage statistics and analysis
- 🤖 **Agent Monitor** - AI Agent runtime status monitoring
- 🎯 **Skills Manager** - AI skills scanning and management
- 💎 **Core Assets** - Knowledge asset management and retrieval

## Tech Stack

### Backend
- **FastAPI** - Modern Python web framework
- **SQLAlchemy** - Database ORM
- **SQLite** - Database (can be configured to use PostgreSQL/MySQL)
- **JWT Authentication** - Secure token-based authentication

### Frontend
- **React** - UI framework
- **TypeScript** - Type safety
- **Tailwind CSS** - Utility-first CSS framework
- **Vite** - Fast build tool

## Project Structure

```
workbench/
├── backend/
│   ├── auth/                    # Authentication module
│   ├── tools/                   # Tool modules
│   │   ├── wsl_path_bridge/     # WSL path conversion tool
│   │   ├── ai_session_manager/  # AI session manager
│   │   ├── chat_records/        # Chat records manager
│   │   │   ├── backup.py        # Incremental backup + delete source
│   │   │   ├── database.py      # Unified data model + FTS search
│   │   │   ├── importers/       # WeChat/QQ/Feishu data importers
│   │   │   └── routes/          # API routes
│   │   ├── usage_monitor/       # Usage monitoring
│   │   ├── agent_monitor/       # Agent monitoring
│   │   ├── skills_manager/      # Skills management
│   │   └── core_assets/         # Core assets
│   ├── main.py                  # Main FastAPI application
│   └── database.py              # Database configuration
├── frontend/                    # React frontend
├── scripts/                     # Helper scripts
│   ├── decrypt_wechat.py        # WeChat database decryption tool
│   └── decrypt_qq.py            # QQ database decryption tool
└── README.md
```

## Chat Records Management

Supports WeChat, QQ, and Feishu chat history management.

### Workflow

1. **One-click Backup** - Incrementally or fully backup encrypted database files to `D:\backup\chat-records\{platform}\`
2. **Import Chat Info** - Decrypt databases from backup directory, import into workbench.db (supports time range filtering)
3. **Search & Browse** - Full-text search, contact browsing, message viewing, statistics
4. **Delete Source Data** - Optionally delete source data after successful backup (with confirmation)

### Backup Modes

- **增量 (Incremental)** - Compares file `mtime + size` to only copy new or changed files (default)
- **全量 (Full)** - Force re-copy all files, ignoring existing backup

### Import Time Range

When importing chat records, you can filter by time range:
- 全部 (All) - Import all messages
- 今天 (Today) - Last 24 hours
- 最近三天 (3 Days) - Last 3 days
- 最近一周 (Week) - Last 7 days
- 最近一个月 (Month) - Last 30 days

The import progress shows percentage and imported message count. After completion, it displays detailed session information including message counts per conversation.

### Data Decryption

WeChat and QQ use SQLCipher-encrypted databases. Decryption scripts must run on **Windows**:

```bash
# Extract key (requires WeChat/QQ to be running)
python scripts/decrypt_wechat.py --extract-key

# Decrypt backed-up databases
python scripts/decrypt_wechat.py --decrypt-all --input "D:\backup\chat-records\wechat"
```

Feishu uses the official API (requires `FEISHU_APP_ID` / `FEISHU_APP_SECRET`).

### Environment Variables

```env
CHAT_BACKUP_DIR=D:\backup\chat-records    # Backup root directory
WECHAT_DB_KEY=                             # WeChat decryption key (optional)
QQ_DB_KEY=                                 # QQ decryption key (optional)
FEISHU_APP_ID=                             # Feishu app ID (optional)
FEISHU_APP_SECRET=                         # Feishu app secret (optional)
```

## Installation

### Prerequisites
- Python 3.8+
- Node.js 16+

### Quick Start

```bash
./start.sh
```

### Manual Setup

#### Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

#### Frontend

```bash
cd frontend
npm install
npm run dev
```

## Usage

1. Access the application at `http://localhost:5173`
2. Register a new account or login with existing credentials
3. Browse available tools in the sidebar
4. Click "💬 聊天记录" to enter the Chat Records management page

## API Endpoints

### Authentication
- `POST /api/auth/register` - User registration
- `POST /api/auth/login` - User login
- `GET /api/auth/me` - Get current user info

### Tools
- `GET /api/tools` - List all available tools
- `GET /api/health` - Health check

### Chat Records
- `POST /api/tools/chat_records/backup/{platform}/execute` - One-click backup
- `POST /api/tools/chat_records/backup/{platform}/delete-source` - Delete source data
- `GET /api/tools/chat_records/sources` - Data source status
- `GET /api/tools/chat_records/contacts` - Contact list
- `GET /api/tools/chat_records/conversations` - Conversation list
- `GET /api/tools/chat_records/messages/conversation/{id}` - Message list
- `GET /api/tools/chat_records/search?q=xxx` - Full-text search
- `GET /api/tools/chat_records/stats/overview` - Statistics overview

### Theme
- `GET /api/theme` - Get user theme preference
- `POST /api/theme` - Update user theme preference

## Development

### Adding New Tools

To add a new tool:

1. Create a new directory under `backend/tools/`
2. Add `router.py` with FastAPI APIRouter
3. Add `meta.json` with tool metadata
4. The tool will be automatically discovered and registered

Example `meta.json`:
```json
{
  "name": "My Tool",
  "id": "my_tool",
  "description": "Description of my tool",
  "icon": "🔧",
  "category": "Development",
  "version": "1.0.0"
}
```

## License

MIT License