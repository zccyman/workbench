import { useState, useEffect, useCallback } from 'react';
import { BarChart3 } from 'lucide-react';
import api from '../../utils/api';
import { ConfigPanel } from '../../components/usage_monitor/ConfigPanel';
import { SummaryCards } from '../../components/usage_monitor/SummaryCards';
import { ToolFrequencyChart } from '../../components/usage_monitor/ToolFrequencyChart';
import { SkillFrequencyChart } from '../../components/usage_monitor/SkillFrequencyChart';
import { HourlyHeatmap } from '../../components/usage_monitor/HourlyHeatmap';
import { DailyActivityChart } from '../../components/usage_monitor/DailyActivityChart';

type TimePeriod = 'all' | 'daily' | 'weekly' | 'monthly';

interface UsageData {
  summary: { total_sessions: number; total_tool_calls: number; total_skill_reads: number; date_range_from: string; date_range_to: string };
  tool_frequency: Array<{ tool_name: string; calls: number; percentage: number }>;
  skill_frequency: Array<{ skill_name: string; activations: number }>;
  hourly_distribution: Array<{ hour: number; calls: number }>;
  daily_activity: Array<{ date: string; sessions: number; tool_calls: number; skill_reads: number }>;
}

export default function UsageMonitor() {
  const [agents, setAgents] = useState<string[]>([]);
  const [selectedAgent, setSelectedAgent] = useState('bot1');
  const [period, setPeriod] = useState<TimePeriod>('all');
  const [fromDate, setFromDate] = useState('');
  const [toDate, setToDate] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [data, setData] = useState<UsageData | null>(null);

  useEffect(() => {
    api.get('/api/tools/usage_monitor/config')
      .then(res => {
        if (res.data.available_agents?.length > 0) {
          setAgents(res.data.available_agents);
          setSelectedAgent(res.data.available_agents[0]);
        }
      })
      .catch(() => {});
  }, []);

  const runAnalysis = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const params = new URLSearchParams({ agent_name: selectedAgent, period });
      if (fromDate) params.set('from_date', fromDate);
      if (toDate) params.set('to_date', toDate);
      const res = await api.get(`/api/tools/usage_monitor/analyze?${params}`);
      setData(res.data);
    } catch (err: any) {
      setError(err.response?.data?.detail || '分析失败，请检查 Agent 目录是否存在');
    } finally {
      setLoading(false);
    }
  }, [selectedAgent, period, fromDate, toDate]);

  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <BarChart3 className="w-7 h-7" style={{ color: '#3b82f6' }} />
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary, #0f172a)' }}>Usage Monitor</h1>
      </div>

      <ConfigPanel
        agents={agents}
        selectedAgent={selectedAgent}
        onAgentChange={setSelectedAgent}
        period={period}
        onPeriodChange={setPeriod}
        fromDate={fromDate}
        toDate={toDate}
        onFromDateChange={setFromDate}
        onToDateChange={setToDate}
        onAnalyze={runAnalysis}
        loading={loading}
      />

      {error && (
        <div className="mb-6 p-4 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-lg">{error}</div>
      )}

      {data && (
        <>
          <SummaryCards
            totalSessions={data.summary.total_sessions}
            totalToolCalls={data.summary.total_tool_calls}
            totalSkillReads={data.summary.total_skill_reads}
            dateRange={`${data.summary.date_range_from} ~ ${data.summary.date_range_to}`}
          />

          {data.tool_frequency.length === 0 && data.skill_frequency.length === 0 && (
            <div className="text-center py-12" style={{ color: 'var(--text-secondary, #64748b)' }}>
              未找到数据。请确认 Agent 目录正确，或选择更广的时间范围。
            </div>
          )}

          {data.tool_frequency.length > 0 && <ToolFrequencyChart data={data.tool_frequency} />}
          {data.skill_frequency.length > 0 && <SkillFrequencyChart data={data.skill_frequency} />}
          <HourlyHeatmap data={data.hourly_distribution} />
          <DailyActivityChart data={data.daily_activity} />
        </>
      )}

      {!data && !loading && !error && (
        <div className="text-center py-16" style={{ color: 'var(--text-secondary, #64748b)' }}>
          <BarChart3 className="w-12 h-12 mx-auto mb-4 opacity-40" />
          <p className="text-lg font-medium">选择配置后点击「分析」</p>
          <p className="text-sm mt-1">将分析 OpenClaw 会话的工具调用和技能激活情况</p>
        </div>
      )}
    </div>
  );
}
