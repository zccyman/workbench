import { Outlet, Link, useNavigate } from 'react-router-dom'
import { useState, useEffect } from 'react'
import api from '../utils/api'

interface LayoutProps {
  dark: boolean
  setDark: (d: boolean) => void
}

export default function Layout({ dark, setDark }: LayoutProps) {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')

  useEffect(() => {
    api.get('/api/auth/me').then(res => {
      setUsername(res.data.username)
    }).catch(() => {
      localStorage.removeItem('token')
      navigate('/login')
    })
  }, [navigate])

  const handleLogout = () => {
    localStorage.removeItem('token')
    navigate('/login')
  }

  return (
    <div className="min-h-screen flex">
      <aside className="w-60 border-r p-4 flex flex-col" style={{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border)' }}>
        <Link to="/" className="text-xl font-bold mb-6">🛠️ Workbench</Link>
        <nav className="flex-1 space-y-1">
          <Link to="/" className="block px-3 py-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700">🏠 首页</Link>
          <Link to="/tools/wsl-path-bridge" className="block px-3 py-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700">📂 WSL 路径转换</Link>
          <Link to="/tools/skills_manager" className="block px-3 py-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700">🎯 技能管理</Link>
          <Link to="/tools/core_assets" className="block px-3 py-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700">💎 核心资产</Link>
          <Link to="/tools/ai_session_manager" className="block px-3 py-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700">🤖 AI 会话</Link>
          <Link to="/tools/chat_records" className="block px-3 py-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700">💬 聊天记录</Link>
        </nav>
        <div className="border-t pt-3 space-y-2" style={{ borderColor: 'var(--border)' }}>
          {username && (
            <div className="px-3 py-2 text-sm" style={{ color: 'var(--text-secondary)' }}>
              👤 {username}
            </div>
          )}
          <button onClick={() => setDark(!dark)} className="w-full text-left px-3 py-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700">
            {dark ? '☀️ 亮色' : '🌙 暗色'}
          </button>
          <button onClick={handleLogout} className="w-full text-left px-3 py-2 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-red-500">
            🚪 退出
          </button>
        </div>
      </aside>
      <main className="flex-1 p-6 overflow-auto">
        <Outlet />
      </main>
    </div>
  )
}
