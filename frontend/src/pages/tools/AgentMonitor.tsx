import { Activity } from 'lucide-react';
import { DashboardOverview } from '../../components/agent_monitor/DashboardOverview';
import { AgentStatusCard } from '../../components/agent_monitor/AgentStatusCard';
import { TokenChart } from '../../components/agent_monitor/TokenChart';
import { CostChart } from '../../components/agent_monitor/CostChart';
import { ModelPieChart } from '../../components/agent_monitor/ModelPieChart';
import { SessionTimeline } from '../../components/agent_monitor/SessionTimeline';

export default function AgentMonitor() {
  return (
    <div>
      <div className="flex items-center gap-3 mb-6">
        <Activity className="w-7 h-7" style={{ color: '#3b82f6' }} />
        <h1 className="text-2xl font-bold" style={{ color: 'var(--text-primary, #0f172a)' }}>
          Agent Monitor
        </h1>
      </div>

      <DashboardOverview />

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mt-6">
        <div className="lg:col-span-1">
          <AgentStatusCard />
        </div>
        <div className="lg:col-span-3">
          <TokenChart />
        </div>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-4 gap-6 mt-6">
        <div className="lg:col-span-1">
          <ModelPieChart />
        </div>
        <div className="lg:col-span-3">
          <CostChart />
        </div>
      </div>

      <div className="mt-6">
        <SessionTimeline />
      </div>
    </div>
  );
}
