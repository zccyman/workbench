import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface HourlyHeatmapProps {
  data: Array<{ hour: number; calls: number }>;
}

export function HourlyHeatmap({ data }: HourlyHeatmapProps) {
  return (
    <div className="p-4 rounded-xl border mb-6" style={{ borderColor: 'var(--border, #e2e8f0)', backgroundColor: 'var(--bg-primary, #f8fafc)' }}>
      <h3 className="text-sm font-semibold mb-4" style={{ color: 'var(--text-primary, #0f172a)' }}>
        🕐 Hourly Distribution
      </h3>
      <ResponsiveContainer width="100%" height={200}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="var(--border, #e2e8f0)" />
          <XAxis dataKey="hour" stroke="var(--text-secondary, #64748b)" fontSize={11} tickFormatter={(v) => `${v}:00`} />
          <YAxis stroke="var(--text-secondary, #64748b)" fontSize={12} />
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
            labelFormatter={(label) => `${label}:00`}
          />
          <Bar dataKey="calls" fill="#8b5cf6" radius={[2, 2, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}
