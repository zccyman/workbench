import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

interface DailyActivityChartProps {
  data: Array<{ date: string; sessions: number; tool_calls: number; skill_reads: number }>;
}

export function DailyActivityChart({ data }: DailyActivityChartProps) {
  if (data.length === 0) return null;

  return (
    <div className="p-4 rounded-xl border mb-6" style={{ borderColor: 'var(--border, #e2e8f0)', backgroundColor: 'var(--bg-primary, #f8fafc)' }}>
      <h3 className="text-sm font-semibold mb-4" style={{ color: 'var(--text-primary, #0f172a)' }}>
        📅 Daily Activity
      </h3>
      <ResponsiveContainer width="100%" height={250}>
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border, #e2e8f0)" />
          <XAxis dataKey="date" stroke="var(--text-secondary, #64748b)" fontSize={11} />
          <YAxis stroke="var(--text-secondary, #64748b)" fontSize={12} />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--bg-secondary, #fff)',
              border: '1px solid var(--border, #e2e8f0)',
              borderRadius: '8px',
              fontSize: '12px',
            }}
          />
          <Legend wrapperStyle={{ fontSize: '12px' }} />
          <Line type="monotone" dataKey="sessions" stroke="#3b82f6" strokeWidth={2} dot={{ r: 3 }} name="Sessions" />
          <Line type="monotone" dataKey="tool_calls" stroke="#10b981" strokeWidth={2} dot={{ r: 3 }} name="Tool Calls" />
          <Line type="monotone" dataKey="skill_reads" stroke="#f59e0b" strokeWidth={2} dot={{ r: 3 }} name="Skill Reads" />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
}
