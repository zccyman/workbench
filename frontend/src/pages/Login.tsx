import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../utils/api'

export default function Login() {
  const [isRegister, setIsRegister] = useState(false)
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [error, setError] = useState('')
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    try {
      const url = isRegister ? '/api/auth/register' : '/api/auth/login'
      const res = await api.post(url, { username, password })
      if (isRegister) {
        setError('')
        setIsRegister(false)
        alert('注册成功！请登录')
      } else if (res.data.token) {
        localStorage.setItem('token', res.data.token)
        navigate('/')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '操作失败')
    }
  }

  return (
    <div className="min-h-screen flex items-center justify-center" style={{ backgroundColor: 'var(--bg-secondary)' }}>
      <div className="w-full max-w-sm p-8 rounded-lg shadow" style={{ backgroundColor: 'var(--bg-primary)' }}>
        <h1 className="text-2xl font-bold text-center mb-6">🛠️ Workbench</h1>
        {error && <div className="bg-red-100 text-red-700 p-2 rounded mb-4 text-sm">{error}</div>}
        <form onSubmit={handleSubmit} className="space-y-4">
          <input
            type="text" placeholder="用户名" value={username} onChange={(e) => setUsername(e.target.value)}
            className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            style={{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border)' }}
            required
          />
          <input
            type="password" placeholder="密码" value={password} onChange={(e) => setPassword(e.target.value)}
            className="w-full px-4 py-2 border rounded focus:outline-none focus:ring-2 focus:ring-blue-500"
            style={{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border)' }}
            required
          />
          <button type="submit" className="w-full py-2 bg-blue-600 text-white rounded hover:bg-blue-700">
            {isRegister ? '注册' : '登录'}
          </button>
        </form>
        <p className="text-center text-sm mt-4" style={{ color: 'var(--text-secondary)' }}>
          {isRegister ? '已有账号？' : '没有账号？'}
          <button onClick={() => setIsRegister(!isRegister)} className="text-blue-600 ml-1">
            {isRegister ? '登录' : '注册'}
          </button>
        </p>
      </div>
    </div>
  )
}
