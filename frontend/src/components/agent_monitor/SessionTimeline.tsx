import { useState, useEffect } from 'react';
import { Clock } from 'lucide-react';
import api from '../../utils/api';

interface Session {
  session_id: string;
  project_name: string | null;
  agent_type: string;
  model: string | null;
  start_time: string | null;
  message_count: number;
  estimated_tokens: number;
  estimated_cost: number;
}

function formatTokens(tokens: number): string {
  if (tokens >= 1_000_000) return `${(tokens / 1_000_000).toFixed(1)}M`;
  if (tokens >= 1_000) return `${(tokens / 1_000).toFixed(0)}K`;
  return `${tokens}`;
}

function timeAgo(dateStr: string | null): string {
  if (!dateStr) return '未知';
  try {
    const diff = Date.now() - new Date(dateStr).getTime();
    const mins = Math.floor(diff / 60000);
    if (mins < 1) return '刚刚';
    if (mins < 60) return `${mins} 分钟前`;
    const hours = Math.floor(mins / 60);
    if (hours < 24) return `${hours} 小时前`;
    return `${Math.floor(hours / 24)} 天前`;
  } catch {
    return dateStr.slice(0, 16);
  }
}

function SessionList({ sessions, label }: { sessions: Session[]; label: string }) {
  if (sessions.length === 0) {
    return (
      <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-4">{label}</h3>
        <p className="text-center text-gray-400 py-8">暂无会话</p>
      </div>
    );
  }

  return (
    <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-4">
        {label} <span className="text-xs text-gray-400">({sessions.length})</span>
      </h3>
      <div className="space-y-2 max-h-96 overflow-y-auto">
        {sessions.map(session => (
          <div
            key={session.session_id}
            className="flex items-center justify-between p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50 hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
          >
            <div className="flex items-center gap-3 min-w-0">
              <Clock className="w-4 h-4 text-gray-400 flex-shrink-0" />
              <div className="min-w-0">
                <div className="text-sm font-medium truncate" style={{ color: 'var(--text-primary, #0f172a)' }}>
                  {session.project_name || 'Unknown'}
                </div>
                <div className="text-xs text-gray-500 dark:text-gray-400">
                  {session.model || 'unknown model'}
                </div>
              </div>
            </div>
            <div className="text-right flex-shrink-0 ml-4">
              <div className="text-xs text-gray-500 dark:text-gray-400">{timeAgo(session.start_time)}</div>
              <div className="text-xs text-gray-400 dark:text-gray-500">
                {session.message_count} msgs · {formatTokens(session.estimated_tokens)} · ${session.estimated_cost.toFixed(4)}
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function SessionTimeline() {
  const [kiloSessions, setKiloSessions] = useState<Session[]>([]);
  const [openSessions, setOpenSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([
      api.get('/api/tools/agent_monitor/sessions?agent=kilocode&limit=20'),
      api.get('/api/tools/agent_monitor/sessions?agent=opencode&limit=20'),
    ])
      .then(([kiloRes, openRes]) => {
        setKiloSessions(kiloRes.data.sessions || []);
        setOpenSessions(openRes.data.sessions || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {[1, 2].map(i => (
          <div key={i} className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
            <div className="space-y-3">
              {[1, 2, 3].map(j => (
                <div key={j} className="animate-pulse h-14 bg-gray-100 dark:bg-gray-700 rounded" />
              ))}
            </div>
          </div>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
      <SessionList sessions={kiloSessions} label="KiloCode 会话" />
      <SessionList sessions={openSessions} label="OpenCode 会话" />
    </div>
  );
}
