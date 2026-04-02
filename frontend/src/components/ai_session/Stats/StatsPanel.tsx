import { BarChart3, TrendingUp, Folder } from 'lucide-react';

interface StatsPanelProps {
  overview: any;
  trends: any[];
  projectStats: any[];
  loading: boolean;
}

export function StatsPanel({ overview, projectStats, loading }: StatsPanelProps) {
  if (loading) return <div className="text-center py-8 text-gray-500 dark:text-gray-400">Loading...</div>;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400 text-xs mb-2"><TrendingUp className="w-3.5 h-3.5" />总消息数</div>
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{overview?.total_messages?.toLocaleString() || 0}</p>
        </div>
        <div className="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400 text-xs mb-2"><BarChart3 className="w-3.5 h-3.5" />总会话数</div>
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{overview?.total_sessions || 0}</p>
        </div>
        <div className="bg-white dark:bg-gray-900 rounded-xl p-4 border border-gray-200 dark:border-gray-700">
          <div className="flex items-center gap-2 text-gray-500 dark:text-gray-400 text-xs mb-2"><Folder className="w-3.5 h-3.5" />项目数</div>
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{overview?.total_projects || 0}</p>
        </div>
      </div>

      {projectStats && projectStats.length > 0 && (
        <div className="bg-white dark:bg-gray-900 rounded-xl border border-gray-200 dark:border-gray-700 p-4">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3">项目分布</h3>
          <div className="space-y-2">
            {projectStats.slice(0, 10).map((p: any, i: number) => (
              <div key={i} className="flex items-center gap-3">
                <span className="text-sm text-gray-600 dark:text-gray-400 w-32 truncate">{p.name || p.project_id}</span>
                <div className="flex-1 bg-gray-100 dark:bg-gray-800 rounded-full h-2">
                  <div className="bg-blue-500 rounded-full h-2" style={{ width: `${Math.min((p.session_count / (projectStats[0]?.session_count || 1)) * 100, 100)}%` }} />
                </div>
                <span className="text-xs text-gray-500 dark:text-gray-400 w-12 text-right">{p.session_count}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
