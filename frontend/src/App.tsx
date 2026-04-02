import { Routes, Route, Navigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import Layout from './components/Layout'
import Home from './pages/Home'
import Login from './pages/Login'
import ProtectedRoute from './components/ProtectedRoute'
import WslPathBridge from './pages/tools/WslPathBridge'

// 动态工具组件映射
const toolComponents: Record<string, React.ComponentType> = {
  'wsl-path-bridge': WslPathBridge,
  'wsl_path_bridge': WslPathBridge,
}

function App() {
  const [dark, setDark] = useState(() => {
    const saved = localStorage.getItem('theme')
    return saved === 'dark'
  })

  useEffect(() => {
    document.documentElement.classList.toggle('dark', dark)
    localStorage.setItem('theme', dark ? 'dark' : 'light')
  }, [dark])

  // 动态工具页面组件
  const ToolPage = ({ toolId }: { toolId: string }) => {
    // 尝试多种ID格式匹配
    const Component = toolComponents[toolId] || toolComponents[toolId.replace(/-/g, '_')]
    
    if (Component) {
      return <Component />
    }
    
    return (
      <div className="text-center py-8">
        <h2 className="text-xl font-semibold">工具未找到</h2>
        <p className="mt-2" style={{ color: 'var(--text-secondary)' }}>
          未找到ID为 "{toolId}" 的工具
        </p>
      </div>
    )
  }

  return (
    <Routes>
      <Route path="/login" element={<Login />} />
      <Route path="/" element={<ProtectedRoute><Layout dark={dark} setDark={setDark} /></ProtectedRoute>}>
        <Route index element={<Home />} />
        {/* 动态工具路由 */}
        <Route path="tools/:toolId" element={<ToolPage />} />
      </Route>
      <Route path="*" element={<Navigate to="/" />} />
    </Routes>
  )
}

export default App