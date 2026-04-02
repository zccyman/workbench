import { useState, useEffect } from 'react';
import api from '../../utils/api';

interface Session {
  id: string;
  project_name: string;
  directory: string;
  message_count: number;
  created_at: number;
  updated_at: number;
  source: string;
}

interface SessionDetail {
  id: string;
  project_name: string;
  messages: { role: string; content: string; timestamp: number }[];
}

export default function AiSessionManager() {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [selectedSession, setSelectedSession] = useState<SessionDetail | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [searchQuery, setSearchQuery] = useState('');
  const [source, setSource] = useState('kilo');

  const BASE = '/api/tools/ai_session_manager';

  useEffect(() => {
    fetchSessions();
  }, [source]);

  const fetchSessions = async () => {
    setLoading(true);
    setError('');
    try {
      const res = await api.get(`${BASE}/sessions`, { params: { source, limit: 100 } });
      setSessions(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || '加载会话失败');
    } finally {
      setLoading(false);
    }
  };

  const fetchSessionDetail = async (id: string) => {
    try {
      const res = await api.get(`${BASE}/messages/session/${id}`, { params: { source } });
      setSelectedSession({ id, project_name: '', messages: res.data });
    } catch (err: any) {
      setError(err.response?.data?.detail || '加载消息失败');
    }
  };

  const handleSearch = async () => {
    if (!searchQuery.trim()) return;
    setLoading(true);
    try {
      const res = await api.get(`${BASE}/search`, { params: { q: searchQuery, source } });
      setSessions(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || '搜索失败');
    } finally {
      setLoading(false);
    }
  };

  const timeAgo = (ts: number) => {
    if (!ts) return '';
    const d = new Date(ts);
    return d.toLocaleDateString('zh-CN');
  };

  return (
    <div className="flex h-full">
      {/* 左侧：会话列表 */}
      <div className="w-80 border-r flex flex-col" style={{ borderColor: 'var(--border)' }}>
        <div className="p-3 border-b" style={{ borderColor: 'var(--border)' }}>
          <div className="flex gap-2">
            <input
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              onKeyDown={(e) => e.key === 'Enter' && handleSearch()}
              placeholder="搜索会话..."
              className="flex-1 px-3 py-1.5 text-sm border rounded"
              style={{ borderColor: 'var(--border)' }}
            />
            <button onClick={handleSearch} className="px-3 py-1.5 text-sm bg-blue-600 text-white rounded hover:bg-blue-700">
              搜索
            </button>
          </div>
          <div className="flex gap-2 mt-2">
            <button
              onClick={() => setSource('kilo')}
              className={`px-2 py-1 text-xs rounded ${source === 'kilo' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100'}`}
            >
              Kilo Code
            </button>
            <button
              onClick={() => setSource('opencode')}
              className={`px-2 py-1 text-xs rounded ${source === 'opencode' ? 'bg-blue-100 text-blue-700' : 'bg-gray-100'}`}
            >
              OpenCode
            </button>
            <button onClick={fetchSessions} className="ml-auto text-xs text-blue-600">
              刷新
            </button>
          </div>
        </div>

        <div className="flex-1 overflow-auto">
          {loading ? (
            <div className="text-center py-8 text-sm" style={{ color: 'var(--text-secondary)' }}>加载中...</div>
          ) : error ? (
            <div className="text-center py-8 text-sm text-red-500">{error}</div>
          ) : sessions.length === 0 ? (
            <div className="text-center py-8 text-sm" style={{ color: 'var(--text-secondary)' }}>暂无会话</div>
          ) : (
            sessions.map((s) => (
              <div
                key={s.id}
                onClick={() => fetchSessionDetail(s.id)}
                className="px-3 py-2 border-b cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800"
                style={{ borderColor: 'var(--border)' }}
              >
                <p className="text-sm font-medium truncate">{s.project_name || 'Unknown'}</p>
                <div className="flex gap-2 mt-1 text-xs" style={{ color: 'var(--text-secondary)' }}>
                  <span>{s.message_count} 条消息</span>
                  <span>{timeAgo(s.updated_at)}</span>
                </div>
              </div>
            ))
          )}
        </div>
      </div>

      {/* 右侧：消息详情 */}
      <div className="flex-1 overflow-auto p-4">
        {selectedSession ? (
          <div className="space-y-3">
            <h3 className="text-lg font-semibold">会话详情</h3>
            {selectedSession.messages.map((msg, i) => (
              <div
                key={i}
                className={`p-3 rounded-lg text-sm ${
                  msg.role === 'user'
                    ? 'bg-blue-50 dark:bg-blue-900/20 ml-12'
                    : 'bg-gray-50 dark:bg-gray-800 mr-12'
                }`}
              >
                <p className="text-xs font-semibold mb-1" style={{ color: 'var(--text-secondary)' }}>
                  {msg.role === 'user' ? '👤 用户' : '🤖 助手'}
                </p>
                <div className="whitespace-pre-wrap">{msg.content}</div>
              </div>
            ))}
          </div>
        ) : (
          <div className="flex items-center justify-center h-full" style={{ color: 'var(--text-secondary)' }}>
            <div className="text-center">
              <p className="text-4xl mb-3">🤖</p>
              <p>选择一个会话查看详情</p>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
