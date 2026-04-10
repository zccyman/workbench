# Workbench - 个人工具箱网站

Workbench 是一个开源的个人工具箱网站，使用 FastAPI + React + TypeScript + Tailwind CSS + Vite 构建。

## 功能特性

- 🔐 **认证系统** - 安全的用户注册和登录
- 🛠️ **工具自动发现** - 自动发现和注册工具
- 📁 **WSL 路径桥接** - 浏览 WSL 文件系统并在 WSL 和 Windows 路径格式间转换
- 🎨 **主题支持** - 支持浅色和深色主题
- 📊 **工具管理** - 带有元数据的集中式工具注册表
- 🤖 **AI 会话管理** - 浏览、搜索、导出 Kilo Code / OpenCode 的 AI 编码会话
- 💬 **聊天记录管理** - 微信 / QQ / 飞书聊天记录的一键备份、解密导入、搜索查询
- 📊 **使用监控** - AI 工具使用量统计与分析
- 🤖 **Agent 监控** - AI Agent 运行状态监控
- 🎯 **技能管理** - AI 技能的扫描与管理
- 💎 **核心资产** - 知识资产的管理与检索

## 技术栈

### 后端
- **FastAPI** - 现代 Python Web 框架
- **SQLAlchemy** - 数据库 ORM
- **SQLite** - 数据库（可配置为使用 PostgreSQL/MySQL）
- **JWT 认证** - 安全的基于令牌的认证

### 前端
- **React** - UI 框架
- **TypeScript** - 类型安全
- **Tailwind CSS** - 实用优先的 CSS 框架
- **Vite** - 快速构建工具

## 项目结构

```
workbench/
├── backend/
│   ├── auth/                    # 认证模块
│   ├── tools/                   # 工具模块
│   │   ├── wsl_path_bridge/     # WSL 路径转换工具
│   │   ├── ai_session_manager/  # AI 会话管理器
│   │   ├── chat_records/        # 聊天记录管理器
│   │   │   ├── backup.py        # 增量备份 + 删除源数据
│   │   │   ├── database.py      # 统一数据模型 + FTS 搜索
│   │   │   ├── importers/       # 微信/QQ/飞书数据导入
│   │   │   └── routes/          # API 路由
│   │   ├── usage_monitor/       # 使用监控
│   │   ├── agent_monitor/       # Agent 监控
│   │   ├── skills_manager/      # 技能管理
│   │   └── core_assets/         # 核心资产
│   ├── main.py                  # 主 FastAPI 应用
│   └── database.py              # 数据库配置
├── frontend/                    # React 前端
├── scripts/                     # 辅助脚本
│   ├── decrypt_wechat.py        # 微信数据库解密工具
│   └── decrypt_qq.py            # QQ 数据库解密工具
└── README.md
```

## 聊天记录管理

支持微信、QQ、飞书三个平台的聊天记录管理：

### 工作流程

1. **一键备份** - 将原始加密数据库文件增量备份到 `D:\backup\chat-records\{platform}\`
2. **解密导入** - 从备份目录解密数据库，导入到 workbench.db 统一数据模型
3. **搜索查询** - 支持全文搜索、联系人浏览、消息查看、统计概览
4. **删除源数据** - 备份成功后可选择删除源数据释放磁盘空间（带二次确认）

### 增量备份

基于文件 `mtime + size` 对比，只复制新增或变更的文件，跳过未变文件。

### 数据解密

微信和 QQ 的本地数据库使用 SQLCipher 加密，需要在 **Windows 侧**运行解密脚本：

```bash
# 提取密钥（需微信/QQ 正在运行）
python scripts/decrypt_wechat.py --extract-key

# 解密备份的数据库
python scripts/decrypt_wechat.py --decrypt-all --input "D:\backup\chat-records\wechat"
```

飞书通过官方 API 获取数据（需配置 `FEISHU_APP_ID` / `FEISHU_APP_SECRET`）。

### 环境变量

```env
CHAT_BACKUP_DIR=D:\backup\chat-records    # 备份根目录
WECHAT_DB_KEY=                             # 微信解密密钥（可选）
QQ_DB_KEY=                                 # QQ 解密密钥（可选）
FEISHU_APP_ID=                             # 飞书应用 ID（可选）
FEISHU_APP_SECRET=                         # 飞书应用密钥（可选）
```

## 安装

### 环境要求
- Python 3.8+
- Node.js 16+

### 快速启动

```bash
./start.sh
```

### 手动启动

#### 后端

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn main:app --host 0.0.0.0 --port 8001
```

#### 前端

```bash
cd frontend
npm install
npm run dev
```

## 使用方法

1. 在 `http://localhost:5173` 访问应用
2. 注册新账户或使用现有凭据登录
3. 在侧边栏浏览可用工具
4. 点击「💬 聊天记录」进入聊天记录管理页面

## API 端点

### 认证
- `POST /api/auth/register` - 用户注册
- `POST /api/auth/login` - 用户登录
- `GET /api/auth/me` - 获取当前用户信息

### 工具
- `GET /api/tools` - 列出所有可用工具
- `GET /api/health` - 健康检查

### 聊天记录
- `POST /api/tools/chat_records/backup/{platform}/execute` - 一键备份
- `POST /api/tools/chat_records/backup/{platform}/delete-source` - 删除源数据
- `GET /api/tools/chat_records/sources` - 数据源状态
- `GET /api/tools/chat_records/contacts` - 联系人列表
- `GET /api/tools/chat_records/conversations` - 会话列表
- `GET /api/tools/chat_records/messages/conversation/{id}` - 消息列表
- `GET /api/tools/chat_records/search?q=xxx` - 全文搜索
- `GET /api/tools/chat_records/stats/overview` - 统计概览

### 主题
- `GET /api/theme` - 获取用户主题偏好
- `POST /api/theme` - 更新用户主题偏好

## 开发

### 添加新工具

要添加新工具：

1. 在 `backend/tools/` 下创建新目录
2. 添加带有 FastAPI APIRouter 的 `router.py`
3. 添加带有工具元数据的 `meta.json`
4. 工具将自动被发现和注册

示例 `meta.json`：
```json
{
  "name": "我的工具",
  "id": "my_tool",
  "description": "我的工具描述",
  "icon": "🔧",
  "category": "开发工具",
  "version": "1.0.0"
}
```

## 许可证

MIT 许可证