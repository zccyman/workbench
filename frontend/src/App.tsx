import { Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Layout from './components/Layout'
import Home from './pages/Home'
import Login from './pages/Login'
import ProtectedRoute from './components/ProtectedRoute'
import WslPathBridge from './pages/tools/WslPathBridge'
import AiSessionManager from './pages/tools/AiSessionManager'
import UsageMonitor from './pages/tools/UsageMonitor'
import AgentMonitor from './pages/tools/AgentMonitor'
import SkillsManager from './pages/tools/SkillsManager'
import CoreAssets from './pages/tools/CoreAssets'
import MarkdownViewer from './pages/tools/MarkdownViewer'
import ChatRecords from './pages/tools/ChatRecords'

function App() {
  const [dark, setDark] = useState(() => {
    const saved = localStorage.getItem('theme')
    return saved === 'dark'
  })

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem('theme', dark ? 'dark' : 'light')
  }, [dark])

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<ProtectedRoute><Layout dark={dark} setDark={setDark} /></ProtectedRoute>}>
        <Route index element={<Home />} />
        <Route path="tools/wsl_path_bridge" element={<WslPathBridge />} />
        <Route path="tools/wsl-path-bridge" element={<WslPathBridge />} />
        <Route path="tools/ai_session_manager" element={<AiSessionManager />} />
        <Route path="tools/usage_monitor" element={<UsageMonitor />} />
        <Route path="tools/agent_monitor" element={<AgentMonitor />} />
        <Route path="tools/skills_manager" element={<SkillsManager />} />
        <Route path="tools/core_assets" element={<CoreAssets />} />
        <Route path="tools/markdown_viewer" element={<MarkdownViewer />} />
        <Route path="tools/chat_records" element={<ChatRecords />} />
        <Route path="tools/:toolId" element={<Home />} />
      </Route>
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}

export default App
