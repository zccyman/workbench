import { useState, useEffect } from 'react';
import api from '../../utils/api';

interface Session {
  id: string;
  project_name: string;
  directory: string;
  message_count: number;
  time_updated: number;
}

interface ParsedMessage {
  role: string;
  content: string;
}

export default function AiSessionManager() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [messages, setMessages] = useState<ParsedMessage[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [source, setSource] = useState('kilo');
  const [selectedId, setSelectedId] = useState<string | null>(null);

  const BASE = '/api/tools/ai_session_manager';

  useEffect(() => { fetchSessions(); }, [source]);

  const fetchSessions = async () => {
    setLoading(true); setError(''); setMessages([]); setSelectedId(null);
    try {
      const res = await api.get(`${BASE}/sessions`, { params: { source, limit: 100 } });
      setSessions(res.data);
    } catch (err: any) { setError(err.response?.data?.detail || '加载会话失败'); }
    finally { setLoading(false); }
  };

  const fetchSessionDetail = async (id: string) => {
    setSelectedId(id);
    try {
      const res = await api.get(`${BASE}/messages/session/${id}/with-parts`, { params: { source } });
      const msgs = res.data.map((m: any) => {
        const meta = JSON.parse(m.data || '{}');
        const textParts = (m.parts || [])
          .map((p: any) => { try { return JSON.parse(p.data); } catch { return null; } })
          .filter((p: any) => p && p.type === 'text')
          .map((p: any) => p.text)
          .join('\n');
        return { role: meta.role || '', content: textParts };
      }).filter((m: ParsedMessage) => m.content);
      setMessages(msgs);
    } catch (err: any) { setError(err.response?.data?.detail || '加载消息失败'); }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    try {
      const res = await api.get(`${BASE}/search`, { params: { q: searchQuery, source } });
      setSessions(res.data);
    } catch (err: any) { setError(err.response?.data?.detail || '搜索失败'); }
    finally { setLoading(false); }
  };

  const fmtDate = (ts: number) => ts ? new Date(ts).toLocaleDateString('zh-CN') : '';

  return (
    <div className="flex h-full">
      {/* 左侧会话列表 */}
      <div className="w-80 border-r flex flex-col" style={{ borderColor: 'var(--border)' }}>
        <div className="p-3 border-b" style={{ borderColor: 'var(--border)' }}>
          <div className="flex gap-2">
            <input value={searchQuery} onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()} placeholder="搜索会话..."
              className="flex-1 px-3 py-1.5 text-sm border rounded" style={{ borderColor: 'var(--border)' }} />
            <button onClick={handleSearch} className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">搜索</button>
          </div>
          <div className="flex gap-2 mt-2">
            <button onClick={() => setSource('kilo')}
              className={`px-2 py-1 text-xs rounded ${source === 'kilo' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100'}`}>
              Kilo Code
            </button>
            <button onClick={() => setSource('opencode')}
              className={`px-2 py-1 text-xs rounded ${source === 'opencode' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100'}`}>
              OpenCode
            </button>
            <button onClick={fetchSessions} className="ml-auto text-xs text-blue-600">刷新</button>
          </div>
        </div>

        <div className="flex-1 overflow-auto">
          {loading ? <div className="text-center py-8 text-sm" style={{ color: 'var(--text-secondary)' }}>加载中...</div>
          : error ? <div className="text-center py-8 text-sm text-red-500">{error}</div>
          : sessions.length === 0 ? <div className="text-center py-8 text-sm" style={{ color: 'var(--text-secondary)' }}>暂无会话</div>
          : sessions.map((s) => (
            <div key={s.id} onClick={() => fetchSessionDetail(s.id)}
              className={`px-3 py-2 border-b cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800 ${selectedId === s.id ? 'bg-blue-50 dark:bg-blue-900/20' : ''}`}
              style={{ borderColor: 'var(--border)' }}>
              <p className="text-sm font-medium truncate">{s.project_name || s.directory?.split('/').pop() || 'Unknown'}</p>
              <div className="flex gap-2 mt-1 text-xs" style={{ color: 'var(--text-secondary)' }}>
                <span>{s.message_count} 条消息</span>
                <span>{fmtDate(s.time_updated)}</span>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* 右侧消息详情 */}
      <div className="flex-1 overflow-auto p-4">
        {messages.length > 0 ? (
          <div className="space-y-3">
            {messages.map((msg, i) => (
              <div key={i}
                className={`p-3 rounded-lg text-sm ${
                  msg.role === 'user'
                    ? 'bg-blue-50 dark:bg-blue-900/20 ml-12'
                    : 'bg-gray-50 dark:bg-gray-800 mr-12'
                }`}>
                <p className="text-xs font-semibold mb-1" style={{ color: 'var(--text-secondary)' }}>
                  {msg.role === 'user' ? '👤 用户' : '🤖 助手'}
                </p>
                <div className="whitespace-pre-wrap break-words">{msg.content}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center justify-center h-full" style={{ color: 'var(--text-secondary)' }}>
            <div className="text-center">
              <p className="text-4xl mb-3">🤖</p>
              <p className="text-sm">点击左侧会话查看详情</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
