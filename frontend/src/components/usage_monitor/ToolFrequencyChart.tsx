import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface ToolFrequencyChartProps {
  data: Array<{ tool_name: string; calls: number; percentage: number }>;
}

export function ToolFrequencyChart({ data }: ToolFrequencyChartProps) {
  if (data.length === 0) return null;

  return (
    <div className="p-4 rounded-xl border mb-6" style={{ borderColor: 'var(--border, #e2e8f0)', backgroundColor: 'var(--bg-primary, #f8fafc)' }}>
      <h3 className="text-sm font-semibold mb-4" style={{ color: 'var(--text-primary, #0f172a)' }}>
        🔧 Tool Usage Ranking
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={data.slice(0, 10)} layout="vertical" margin={{ left: 80 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border, #e2e8f0)" />
          <XAxis type="number" stroke="var(--text-secondary, #64748b)" fontSize={12} />
          <YAxis type="category" dataKey="tool_name" stroke="var(--text-secondary, #64748b)" fontSize={12} width={80} />
          <Tooltip
            contentStyle={{
              backgroundColor: 'var(--bg-secondary, #fff)',
              border: '1px solid var(--border, #e2e8f0)',
              borderRadius: '8px',
              fontSize: '12px',
            }}
            formatter={(value: any) => {
              const num = typeof value === 'number' ? value : 0;
              return [`${num} calls`, 'Calls'];
            }}
          />
          <Bar dataKey="calls" fill="#3b82f6" radius={[0, 4, 4, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
