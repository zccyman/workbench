import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'

interface Tool {
  id: string
  name: string
  description: string
  icon: string
  category: string
}

export default function Home() {
  const [tools, setTools] = useState<Tool[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    fetch('/api/tools')
      .then(res => {
        if (!res.ok) throw new Error('Failed to fetch tools')
        return res.json()
      })
      .then(data => {
        setTools(data)
        setLoading(false)
      })
      .catch(err => {
        console.error('Failed to load tools:', err)
        setError('加载工具失败')
        setLoading(false)
      })
  }, [])

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="animate-spin rounded-full h-8 w-8 border-b-2" style={{ borderColor: 'var(--accent)' }}></div>
      </div>
    )
  }

  if (error) {
    return (
      <div className="text-center py-8">
        <p style={{ color: 'var(--error)' }}>{error}</p>
      </div>
    )
  }

  // 按 category 分组
  const categories = [...new Set(tools.map(t => t.category))]

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">我的工具箱</h1>
      
      {categories.map(category => (
        <div key={category} className="mb-8">
          <h2 className="text-lg font-semibold mb-4" style={{ color: 'var(--text-secondary)' }}>
            {category}
          </h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {tools
              .filter(t => t.category === category)
              .map((tool) => (
                <Link
                  key={tool.id}
                  to={`/tools/${tool.id}`}
                  className="block p-6 rounded-lg border hover:shadow-lg transition-shadow"
                  style={{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border)' }}
                >
                  <span className="text-3xl">{tool.icon}</span>
                  <h2 className="text-lg font-semibold mt-2">{tool.name}</h2>
                  <p className="text-sm mt-1" style={{ color: 'var(--text-secondary)' }}>
                    {tool.description}
                  </p>
                </Link>
              ))}
          </div>
        </div>
      ))}
      
      {tools.length === 0 && (
        <p className="text-center" style={{ color: 'var(--text-secondary)' }}>
          暂无可用工具
        </p>
      )}
    </div>
  )
}