# Spec: Markdown 文件查看器与编辑器

> 项目: Workbench 子工具
> 模式: Full (dev-workflow)
> 日期: 2026-04-09

## 一、需求分析

### 核心需求
在 Workbench 个人工具箱网站中新增一个子页面，用于浏览电脑上所有目录的 Markdown 文件，支持：
1. **文件浏览** — 目录树导航，筛选 .md 文件
2. **完美渲染** — Markdown 渲染为精美排版（表格、代码高亮、数学公式、Mermaid图表）
3. **实时编辑** — 左右分栏编辑+预览
4. **保存** — 编辑后保存回原文件

### 用户场景
- 浏览 `/mnt/g/knowledge/` 下的 440+ 篇 wiki 文章
- 快速查看和编辑任意目录的 .md 文件
- 不需要切换到 IDE 即可编辑 Markdown

## 二、技术方案推荐

### 方案对比

| 方案 | 优势 | 劣势 | 推荐度 |
|------|------|------|--------|
| **A: 自研 React 组件** | 完全定制，与 Workbench 深度集成 | 开发量大 | ⭐⭐⭐⭐ |
| B: 嵌入 VS Code Web | 功能最强 | 太重，偏离"轻量工具箱"定位 | ⭐⭐ |
| C: 嵌入 StackEdit/MDUI | 开源可嵌入 | 定制性差，样式难统一 | ⭐⭐ |

### ✅ 推荐：方案A（自研，基于开源组件）

**前端技术栈：**

| 功能 | 组件 | 许可证 |
|------|------|--------|
| Markdown 渲染 | **react-markdown** + remark-gfm | MIT |
| 代码高亮 | **react-syntax-highlighter** (Prism) | MIT |
| 数学公式 | **rehype-katex** + remark-math | MIT |
| Mermaid 图表 | **mermaid** | MIT |
| 编辑器 | **@uiw/react-md-editor** 或 **CodeMirror 6** | MIT |
| 文件树 | 复用 WslPathBridge 的目录浏览组件 | - |

**后端：**
- 复用 FastAPI，新增 3 个 API：
  - `GET /api/tools/markdown_viewer/dir` — 列目录（只显示.md）
  - `GET /api/tools/markdown_viewer/file?path=xxx` — 读取文件内容
  - `PUT /api/tools/markdown_viewer/file` — 保存文件

**布局方案：**
```
┌──────────────────────────────────────┐
│  [目录路径输入] [收藏] [主题切换]       │
├──────────┬───────────────────────────┤
│          │                           │
│  文件树   │   Markdown 渲染 / 编辑    │
│  .md only│   (分栏: 编辑 | 预览)      │
│          │                           │
│          │                           │
├──────────┴───────────────────────────┤
│  状态栏: 文件路径 | 大小 | 行数        │
└──────────────────────────────────────┘
```

### 与现有系统集成
- 路由: `/tools/markdown_viewer`
- 导航: 添加到 Home 页工具列表
- 认证: 复用 ProtectedRoute
- 样式: 复用 Tailwind + dark mode
- 文件浏览: 复用 WslPathBridge 后端逻辑

## 三、任务分解

### Phase 1: 基础功能
1. **后端 API** — 目录列表 + 文件读写
2. **文件树组件** — 目录浏览，.md 筛选
3. **Markdown 渲染** — 基础渲染（标题/列表/表格/代码）
4. **路由集成** — 添加到 App.tsx

### Phase 2: 增强功能
5. **代码高亮** — Prism 语法着色
6. **数学公式** — KaTeX 渲染
7. **Mermaid 图表** — 流程图渲染
8. **编辑器** — CodeMirror 6 编辑 + 实时预览

### Phase 3: 体验优化
9. **收藏/最近文件** — 快速访问常用文件
10. **搜索** — 文件内容搜索
11. **快捷键** — Ctrl+S 保存等

## 四、技术风险

| 风险 | 应对 |
|------|------|
| Mermaid SSR 兼容性 | 使用 dynamic import |
| 大文件性能 | 虚拟滚动 + 懒加载 |
| 文件编码问题 | UTF-8 优先 + BOM 检测 |
| 权限安全 | 路径白名单 + 禁止 .. 跳转 |

---

**请确认方案和任务分解，确认后开始开发。**
