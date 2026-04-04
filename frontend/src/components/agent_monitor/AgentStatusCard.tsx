import { useState, useEffect } from 'react';
import { Circle } from 'lucide-react';
import api from '../../utils/api';

interface Agent {
  name: string;
  type: string;
  status: 'running' | 'idle' | 'offline';
  active_sessions: number;
  last_active: string | null;
  model: string | null;
}

const statusConfig = {
  running: { color: '#22c55e', label: '运行中' },
  idle: { color: '#f59e0b', label: '空闲' },
  offline: { color: '#9ca3af', label: '离线' },
};

export function AgentStatusCard() {
  const [agents, setAgents] = useState<Agent[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/api/tools/agent_monitor/agents')
      .then(res => {
        setAgents(res.data.agents || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Agent 状态</h3>
        <div className="space-y-3">
          {[1, 2].map(i => (
            <div key={i} className="animate-pulse h-16 bg-gray-100 dark:bg-gray-700 rounded" />
          ))}
        </div>
      </div>
    );
  }

  return (
    <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-3">Agent 状态</h3>
      <div className="space-y-3">
        {agents.map(agent => {
          const cfg = statusConfig[agent.status];
          return (
            <div key={agent.type} className="p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50">
              <div className="flex items-center gap-2 mb-1">
                <Circle className="w-3 h-3" fill={cfg.color} stroke={cfg.color} />
                <span className="font-medium" style={{ color: 'var(--text-primary, #0f172a)' }}>{agent.name}</span>
                <span className="text-xs px-2 py-0.5 rounded-full bg-gray-200 dark:bg-gray-600 text-gray-600 dark:text-gray-300">
                  {cfg.label}
                </span>
              </div>
              <div className="text-xs text-gray-500 dark:text-gray-400 space-y-0.5">
                {agent.model && <div>模型：{agent.model}</div>}
                <div>活跃会话：{agent.active_sessions}</div>
                {agent.last_active && <div>最后活跃：{agent.last_active.slice(0, 19)}</div>}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
}
