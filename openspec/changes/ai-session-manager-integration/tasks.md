# AI Session Manager Integration — Tasks

> 状态：大部分已完成，补录中
> 日期：2026-04-03

## Phase 1：后端适配

### Task 1: 创建工具目录和入口文件
- **难度**: 🟢 简单
- **依赖**: 无
- **并行**: ✅ 可并行
- **建议模型**: MiniMax M2.5
- **流程**: 🚢 Ship
- **涉及文件**: `backend/tools/ai_session_manager/__init__.py`, `router.py`, `meta.json`
- **状态**: ✅ 已完成（commit 9b436f2）

### Task 2: 适配 config.py 和 database.py
- **难度**: 🟢 简单
- **依赖**: Task 1
- **并行**: ❌ 串行
- **建议模型**: MiniMax M2.5
- **流程**: 🚢 Ship
- **涉及文件**: `backend/tools/ai_session_manager/config.py`, `database.py`
- **状态**: ✅ 已完成（commit 9b436f2）

### Task 3: 适配 models.py
- **难度**: 🟡 中等
- **依赖**: Task 1
- **并行**: ❌ 串行
- **建议模型**: MiniMax M2.5
- **流程**: 🚢 Ship
- **涉及文件**: `backend/tools/ai_session_manager/models.py`
- **状态**: ✅ 已完成（commit 9b436f2）

### Task 4: 适配所有 routes 模块
- **难度**: 🟡 中等
- **依赖**: Task 1, Task 3
- **并行**: ✅ 可并行（各路由模块独立）
- **建议模型**: MiniMax M2.5
- **流程**: 🚢 Ship
- **涉及文件**: `backend/tools/ai_session_manager/routes/*.py`（8个文件）
- **状态**: ✅ 已完成（commit 9b436f2）

### Task 5: 适配所有 services 模块
- **难度**: 🟡 中等
- **依赖**: Task 1, Task 3
- **并行**: ✅ 可并行
- **建议模型**: MiniMax M2.5
- **流程**: 🚢 Ship
- **涉及文件**: `backend/tools/ai_session_manager/services/*.py`（3个文件）
- **状态**: ✅ 已完成（commit 9b436f2）

## Phase 2：前端适配

### Task 6: 创建 AiSessionManager.tsx 页面
- **难度**: 🟡 中等
- **依赖**: Task 4（API 路由就绪）
- **并行**: ❌ 串行
- **建议模型**: MiniMax M2.5
- **流程**: 👀 Show
- **涉及文件**: `frontend/src/pages/tools/AiSessionManager.tsx`
- **状态**: ✅ 已完成（commit 9b436f2）

### Task 7: 注册到 App.tsx 路由
- **难度**: 🟢 简单
- **依赖**: Task 6
- **并行**: ❌ 串行
- **建议模型**: MiniMax M2.5
- **流程**: 🚢 Ship
- **涉及文件**: `frontend/src/App.tsx`
- **状态**: ✅ 已完成（commit 9b436f2）

## Phase 3：测试

### Task 8: 后端单元测试
- **难度**: 🔴 困难
- **依赖**: Task 4, Task 5
- **并行**: ✅ 可并行（按模块拆分）
- **建议模型**: MiniMax M2.5
- **流程**: 👀 Show
- **涉及文件**: `tests/unit/backend/ai_session_manager/`
- **状态**: ✅ 已完成（100 个测试全部通过）

### Task 9: 前端单元测试
- **难度**: 🟡 中等
- **依赖**: Task 6
- **并行**: ❌ 串行
- **建议模型**: MiniMax M2.5
- **流程**: 👀 Show
- **涉及文件**: `frontend/src/__tests__/AiSessionManager.test.tsx`
- **状态**: ❌ 待补充

## Phase 4：文档

### Task 10: 更新 OpenSpec design.md
- **难度**: 🟢 简单
- **依赖**: 所有实现任务
- **并行**: ❌ 串行
- **建议模型**: MiniMax M2.5
- **流程**: 🚢 Ship
- **涉及文件**: `openspec/design.md`
- **状态**: ❌ 待补充

### Task 11: 更新 .dev-workflow.md
- **难度**: 🟢 简单
- **依赖**: 无
- **并行**: ✅ 可并行
- **建议模型**: MiniMax M2.5
- **流程**: 🚢 Ship
- **涉及文件**: `.dev-workflow.md`
- **状态**: ❌ 待补充

### Task 12: 更新 README 双语文档
- **难度**: 🟢 简单
- **依赖**: 无
- **并行**: ✅ 可并行
- **建议模型**: MiniMax M2.5
- **流程**: 🚢 Ship
- **涉及文件**: `README.md`, `README_CN.md`
- **状态**: ❌ 待补充
