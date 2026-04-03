import { MessageSquare, Wrench, Sparkles } from 'lucide-react';

interface SummaryCardsProps {
  totalSessions: number;
  totalToolCalls: number;
  totalSkillReads: number;
  dateRange: string;
}

export function SummaryCards({ totalSessions, totalToolCalls, totalSkillReads }: SummaryCardsProps) {
  const cards = [
    { icon: MessageSquare, label: 'Sessions', value: totalSessions, color: '#3b82f6' },
    { icon: Wrench, label: 'Tool Calls', value: totalToolCalls, color: '#10b981' },
    { icon: Sparkles, label: 'Skill Reads', value: totalSkillReads, color: '#f59e0b' },
  ];

  return (
    <div className="grid grid-cols-3 gap-4 mb-6">
      {cards.map(({ icon: Icon, label, value, color }) => (
        <div
          key={label}
          className="p-4 rounded-xl border"
          style={{ borderColor: 'var(--border, #e2e8f0)', backgroundColor: 'var(--bg-primary, #f8fafc)' }}
        >
          <div className="flex items-center gap-2 mb-1">
            <Icon className="w-4 h-4" style={{ color }} />
            <span className="text-xs font-medium" style={{ color: 'var(--text-secondary, #64748b)' }}>{label}</span>
          </div>
          <div className="text-2xl font-bold" style={{ color: 'var(--text-primary, #0f172a)' }}>{value}</div>
        </div>
      ))}
    </div>
  );
}
