import { useState, useEffect } from 'react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts';
import api from '../../utils/api';

interface TrendPoint {
  date: string;
  kilocode: number;
  opencode: number;
}

function formatTokens(tokens: number): string {
  if (tokens >= 1_000_000) return `${(tokens / 1_000_000).toFixed(1)}M`;
  if (tokens >= 1_000) return `${(tokens / 1_000).toFixed(0)}K`;
  return `${tokens}`;
}

export function TokenChart() {
  const [data, setData] = useState<TrendPoint[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api.get('/api/tools/agent_monitor/token-trend?period=week')
      .then(res => {
        setData(res.data.data || []);
        setLoading(false);
      })
      .catch(() => setLoading(false));
  }, []);

  if (loading) {
    return (
      <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-4">Token 消耗趋势</h3>
        <div className="h-64 animate-pulse bg-gray-100 dark:bg-gray-700 rounded" />
      </div>
    );
  }

  if (data.length === 0) {
    return (
      <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
        <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-4">Token 消耗趋势</h3>
        <p className="text-center text-gray-400 py-12">暂无数据</p>
      </div>
    );
  }

  return (
    <div className="p-4 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700">
      <h3 className="text-sm font-medium text-gray-500 dark:text-gray-400 mb-4">Token 消耗趋势</h3>
      <ResponsiveContainer width="100%" height={256}>
        <AreaChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} stroke="#9ca3af" />
          <YAxis tick={{ fontSize: 12 }} stroke="#9ca3af" tickFormatter={formatTokens} />
          <Tooltip formatter={(value) => [formatTokens(Number(value)), 'Token']} />
          <Legend />
          <Area type="monotone" dataKey="kilocode" stackId="1" stroke="#3b82f6" fill="#3b82f6" fillOpacity={0.3} name="KiloCode" />
          <Area type="monotone" dataKey="opencode" stackId="1" stroke="#8b5cf6" fill="#8b5cf6" fillOpacity={0.3} name="OpenCode" />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  );
}
