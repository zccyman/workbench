import { useState, useEffect } from 'react';
import { Bot, MessageSquare, Zap, DollarSign } from 'lucide-react';
import api from '../../utils/api';

interface OverviewData {
  active_agents: number;
  total_sessions_today: number;
  estimated_tokens_today: number;
  estimated_cost_today: number;
  most_used_model: string;
}

function formatTokens(tokens: number): string {
  if (tokens >= 1_000_000) return `${(tokens / 1_000_000).toFixed(1)}M`;
  if (tokens >= 1_000) return `${(tokens / 1_000).toFixed(1)}K`;
  return `${tokens}`;
}

const cards = [
  { key: 'active_agents', label: '活跃 Agent', icon: Bot, color: '#22c55e', bg: 'bg-green-50 dark:bg-green-900/20' },
  { key: 'total_sessions_today', label: '今日会话', icon: MessageSquare, color: '#3b82f6', bg: 'bg-blue-50 dark:bg-blue-900/20' },
  { key: 'estimated_tokens_today', label: '今日 Token', icon: Zap, color: '#f59e0b', bg: 'bg-amber-50 dark:bg-amber-900/20' },
  { key: 'estimated_cost_today', label: '今日成本', icon: DollarSign, color: '#ef4444', bg: 'bg-red-50 dark:bg-red-900/20' },
];

export function DashboardOverview() {
  const [data, setData] = useState<OverviewData | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/api/tools/agent_monitor/overview')
      .then(res => {
        setData(res.data);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {cards.map(c => (
          <div key={c.key} className={`p-4 rounded-lg ${c.bg} animate-pulse h-20`} />
        ))}
      </div>
    );
  }

  if (!data) return null;

  const formatValue = (key: string, value: number): string => {
    if (key === 'estimated_tokens_today') return formatTokens(value);
    if (key === 'estimated_cost_today') return `$${value.toFixed(2)}`;
    return `${value}`;
  };

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
      {cards.map(({ key, label, icon: Icon, color, bg }) => {
        const value = data[key as keyof OverviewData];
        return (
          <div key={key} className={`p-4 rounded-lg ${bg} border border-gray-200 dark:border-gray-700`}>
            <div className="flex items-center gap-2 mb-1">
              <Icon className="w-4 h-4" style={{ color }} />
              <span className="text-sm text-gray-500 dark:text-gray-400">{label}</span>
            </div>
            <div className="text-2xl font-bold" style={{ color }}>
              {typeof value === 'number' ? formatValue(key, value) : value}
            </div>
          </div>
        );
      })}
    </div>
  );
}
