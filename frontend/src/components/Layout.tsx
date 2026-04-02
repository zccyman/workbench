import { Outlet, Link, useNavigate } from 'react-router-dom'

interface LayoutProps {
  dark: boolean
  setDark: (d: boolean) => void
}

export default function Layout({ dark, setDark }: LayoutProps) {
  const navigate = useNavigate()

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
        </nav>
        <div className="border-t pt-3 space-y-2" style={{ borderColor: 'var(--border)' }}>
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
