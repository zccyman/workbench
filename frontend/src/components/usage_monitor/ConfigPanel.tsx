import { Search, Calendar, Play } from 'lucide-react';

type TimePeriod = 'all' | 'daily' | 'weekly' | 'monthly';

interface ConfigPanelProps {
  agents: string[];
  selectedAgent: string;
  onAgentChange: (agent: string) => void;
  period: TimePeriod;
  onPeriodChange: (period: TimePeriod) => void;
  fromDate: string;
  toDate: string;
  onFromDateChange: (date: string) => void;
  onToDateChange: (date: string) => void;
  onAnalyze: () => void;
  loading: boolean;
}

export function ConfigPanel({
  agents, selectedAgent, onAgentChange,
  period, onPeriodChange,
  fromDate, toDate, onFromDateChange, onToDateChange,
  onAnalyze, loading,
}: ConfigPanelProps) {
  return (
    <div className="p-4 rounded-xl border mb-6 space-y-4" style={{ borderColor: 'var(--border, #e2e8f0)', backgroundColor: 'var(--bg-primary, #f8fafc)' }}>
      <div className="flex items-center gap-2 mb-2">
        <Search className="w-4 h-4" style={{ color: 'var(--text-secondary, #64748b)' }} />
        <span className="font-semibold text-sm" style={{ color: 'var(--text-secondary, #64748b)' }}>配置</span>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: 'var(--text-secondary, #64748b)' }}>Agent</label>
          <select
            value={selectedAgent}
            onChange={(e) => onAgentChange(e.target.value)}
            className="w-full px-3 py-2 text-sm rounded-lg border focus:outline-none focus:ring-2 focus:ring-blue-500"
            style={{ borderColor: 'var(--border, #e2e8f0)', backgroundColor: 'var(--bg-secondary, #ffffff)', color: 'var(--text-primary, #0f172a)' }}
          >
            {agents.length > 0 ? agents.map(a => (
              <option key={a} value={a}>{a}</option>
            )) : (
              <option value="bot1">bot1</option>
            )}
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: 'var(--text-secondary, #64748b)' }}>
            <Calendar className="w-3 h-3 inline mr-1" /> 时间范围
          </label>
          <select
            value={period}
            onChange={(e) => onPeriodChange(e.target.value as TimePeriod)}
            className="w-full px-3 py-2 text-sm rounded-lg border focus:outline-none focus:ring-2 focus:ring-blue-500"
            style={{ borderColor: 'var(--border, #e2e8f0)', backgroundColor: 'var(--bg-secondary, #ffffff)', color: 'var(--text-primary, #0f172a)' }}
          >
            <option value="all">全部</option>
            <option value="daily">今天</option>
            <option value="weekly">近7天</option>
            <option value="monthly">近30天</option>
          </select>
        </div>

        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: 'var(--text-secondary, #64748b)' }}>开始日期</label>
          <input
            type="date"
            value={fromDate}
            onChange={(e) => onFromDateChange(e.target.value)}
            className="w-full px-3 py-2 text-sm rounded-lg border focus:outline-none focus:ring-2 focus:ring-blue-500"
            style={{ borderColor: 'var(--border, #e2e8f0)', backgroundColor: 'var(--bg-secondary, #ffffff)', color: 'var(--text-primary, #0f172a)' }}
          />
        </div>

        <div>
          <label className="block text-xs font-medium mb-1" style={{ color: 'var(--text-secondary, #64748b)' }}>结束日期</label>
          <input
            type="date"
            value={toDate}
            onChange={(e) => onToDateChange(e.target.value)}
            className="w-full px-3 py-2 text-sm rounded-lg border focus:outline-none focus:ring-2 focus:ring-blue-500"
            style={{ borderColor: 'var(--border, #e2e8f0)', backgroundColor: 'var(--bg-secondary, #ffffff)', color: 'var(--text-primary, #0f172a)' }}
          />
        </div>
      </div>

      <div className="flex justify-end">
        <button
          onClick={onAnalyze}
          disabled={loading}
          className="px-6 py-2 text-sm font-medium rounded-lg flex items-center gap-2 transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          style={{ backgroundColor: '#3b82f6', color: '#ffffff' }}
        >
          <Play className="w-3 h-3" />
          {loading ? '分析中...' : '分析'}
        </button>
      </div>
    </div>
  );
}
