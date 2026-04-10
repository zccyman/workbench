import { useState, useEffect, useMemo } from 'react';
import { Search, Filter, X, FileText, ToggleLeft, ToggleRight, ChevronRight } from 'lucide-react';

const API_BASE = '/api/tools/skills_manager';

interface SkillSummary {
  id: string;
  name: string;
  description: string;
  category: string;
  category_name: string;
  category_icon: string;
  source: string;
  enabled: boolean;
  file_count: number;
  last_modified: string;
}

interface SkillDetail extends SkillSummary {
  skill_md_content: string;
}

interface CategoryStats {
  id: string;
  name: string;
  icon: string;
  count: number;
  enabled_count: number;
}

interface SkillsOverview {
  total: number;
  enabled: number;
  disabled: number;
  categories: CategoryStats[];
}

export default function SkillsManager() {
  const [skills, setSkills] = useState<SkillSummary[]>([]);
  const [overview, setOverview] = useState<SkillsOverview | null>(null);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [sourceFilter, setSourceFilter] = useState('');
  const [detail, setDetail] = useState<SkillDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  useEffect(() => {
    loadData();
  }, [search, categoryFilter, sourceFilter]);

  const loadData = async () => {
    setLoading(true);
    try {
      const params = new URLSearchParams();
      if (search) params.set('search', search);
      if (categoryFilter) params.set('category', categoryFilter);
      if (sourceFilter) params.set('source', sourceFilter);

      const [skillsRes, overviewRes] = await Promise.all([
        fetch(`${API_BASE}/skills?${params}`),
        fetch(`${API_BASE}/categories`),
      ]);
      setSkills(await skillsRes.json());
      setOverview(await overviewRes.json());
    } catch (e) {
      console.error('Failed to load skills:', e);
    } finally {
      setLoading(false);
    }
  };

  const handleToggle = async (skillId: string) => {
    try {
      const res = await fetch(`${API_BASE}/skills/${skillId}/toggle`, { method: 'PATCH' });
      const data = await res.json();
      setSkills(prev => prev.map(s => s.id === skillId ? { ...s, enabled: data.enabled } : s));
      if (detail?.id === skillId) {
        setDetail(prev => prev ? { ...prev, enabled: data.enabled } : null);
      }
      // Refresh overview
      const overviewRes = await fetch(`${API_BASE}/categories`);
      setOverview(await overviewRes.json());
    } catch (e) {
      console.error('Toggle failed:', e);
    }
  };

  const openDetail = async (skillId: string) => {
    setDetailLoading(true);
    try {
      const res = await fetch(`${API_BASE}/skills/${skillId}`);
      setDetail(await res.json());
    } catch (e) {
      console.error('Failed to load detail:', e);
    } finally {
      setDetailLoading(false);
    }
  };

  // 按分类分组
  const grouped = useMemo(() => {
    const groups: Record<string, { name: string; icon: string; skills: SkillSummary[] }> = {};
    for (const s of skills) {
      if (!groups[s.category]) {
        groups[s.category] = { name: s.category_name, icon: s.category_icon, skills: [] };
      }
      groups[s.category].skills.push(s);
    }
    return groups;
  }, [skills]);

  const sourceOptions = ['自研', '开源', '系统内置'];

  return (
    <div className="p-6 max-w-7xl mx-auto">
      {/* Header */}
      <h1 className="text-2xl font-bold mb-6 dark:text-white">🎯 Skills Manager</h1>

      {/* Stats Bar */}
      {overview && (
        <div className="flex gap-4 mb-6 text-sm">
          <span className="px-3 py-1.5 bg-blue-100 dark:bg-blue-900 rounded-lg">
            总计 {overview.total}
          </span>
          <span className="px-3 py-1.5 bg-green-100 dark:bg-green-900 text-green-700 dark:text-green-300 rounded-lg">
            已启用 {overview.enabled}
          </span>
          <span className="px-3 py-1.5 bg-red-100 dark:bg-red-900 text-red-700 dark:text-red-300 rounded-lg">
            已禁用 {overview.disabled}
          </span>
          <span className="px-3 py-1.5 bg-gray-100 dark:bg-gray-700 rounded-lg">
            {overview.categories.length} 个分类
          </span>
        </div>
      )}

      {/* Filters */}
      <div className="flex gap-3 mb-6 flex-wrap">
        {/* Search */}
        <div className="relative flex-1 min-w-[200px]">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400" />
          <input
            type="text"
            placeholder="搜索技能..."
            value={search}
            onChange={e => setSearch(e.target.value)}
            className="w-full pl-10 pr-4 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-600 dark:text-white focus:outline-none focus:ring-2 focus:ring-blue-500"
          />
        </div>
        {/* Category filter */}
        <select
          value={categoryFilter}
          onChange={e => setCategoryFilter(e.target.value)}
          className="px-3 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-600 dark:text-white"
        >
          <option value="">全部分类</option>
          {overview?.categories.map(c => (
            <option key={c.id} value={c.id}>{c.icon} {c.name} ({c.count})</option>
          ))}
        </select>
        {/* Source filter */}
        <select
          value={sourceFilter}
          onChange={e => setSourceFilter(e.target.value)}
          className="px-3 py-2 border rounded-lg dark:bg-gray-800 dark:border-gray-600 dark:text-white"
        >
          <option value="">全部来源</option>
          {sourceOptions.map(s => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>

      {/* Skills Grid by Category */}
      {loading ? (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">加载中...</div>
      ) : Object.keys(grouped).length === 0 ? (
        <div className="text-center py-12 text-gray-500 dark:text-gray-400">没有找到匹配的技能</div>
      ) : (
        Object.entries(grouped).map(([catKey, group]) => (
          <div key={catKey} className="mb-8">
            <h2 className="text-lg font-semibold mb-3 dark:text-white">
              {group.icon} {group.name} ({group.skills.length})
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-4">
              {group.skills.map(skill => (
                <div
                  key={skill.id}
                  className={`border rounded-xl p-4 transition-shadow hover:shadow-md dark:border-gray-700 ${
                    skill.enabled ? 'bg-white dark:bg-gray-800' : 'bg-gray-50 dark:bg-gray-900 opacity-60'
                  }`}
                >
                  <div className="flex items-start justify-between mb-2">
                    <h3 className="font-medium dark:text-white text-sm leading-tight flex-1 mr-2">
                      {skill.name}
                    </h3>
                    <span className={`text-xs px-2 py-0.5 rounded-full shrink-0 ${
                      skill.source === '自研' ? 'bg-purple-100 text-purple-700 dark:bg-purple-900 dark:text-purple-300' :
                      skill.source === '系统内置' ? 'bg-blue-100 text-blue-700 dark:bg-blue-900 dark:text-blue-300' :
                      'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                    }`}>
                      {skill.source}
                    </span>
                  </div>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mb-3 line-clamp-2">
                    {skill.description || '暂无描述'}
                  </p>
                  <div className="flex items-center justify-between text-xs text-gray-400">
                    <span className="flex items-center gap-1">
                      <FileText className="w-3 h-3" /> {skill.file_count} 文件 · {skill.last_modified}
                    </span>
                  </div>
                  <div className="flex items-center justify-between mt-3 pt-3 border-t dark:border-gray-700">
                    <button
                      onClick={() => handleToggle(skill.id)}
                      className="flex items-center gap-1.5 text-sm cursor-pointer"
                    >
                      {skill.enabled ? (
                        <><ToggleRight className="w-5 h-5 text-green-500" /> <span className="text-green-600 dark:text-green-400">已启用</span></>
                      ) : (
                        <><ToggleLeft className="w-5 h-5 text-gray-400" /> <span className="text-gray-500">已禁用</span></>
                      )}
                    </button>
                    <button
                      onClick={() => openDetail(skill.id)}
                      className="flex items-center gap-1 text-sm text-blue-500 hover:text-blue-700 cursor-pointer"
                    >
                      详情 <ChevronRight className="w-3 h-3" />
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        ))
      )}

      {/* Detail Modal */}
      {detail && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4" onClick={() => setDetail(null)}>
          <div
            className="bg-white dark:bg-gray-800 rounded-2xl max-w-3xl w-full max-h-[85vh] flex flex-col shadow-2xl"
            onClick={e => e.stopPropagation()}
          >
            {/* Modal Header */}
            <div className="flex items-center justify-between p-6 border-b dark:border-gray-700">
              <div>
                <h2 className="text-xl font-bold dark:text-white">
                  {detail.category_icon} {detail.name}
                </h2>
                <div className="flex gap-2 mt-1 text-sm text-gray-500">
                  <span>{detail.category_name}</span>
                  <span>·</span>
                  <span>{detail.source}</span>
                  <span>·</span>
                  <span>{detail.file_count} 文件</span>
                  <span>·</span>
                  <span>{detail.last_modified}</span>
                </div>
              </div>
              <div className="flex items-center gap-3">
                <button
                  onClick={() => handleToggle(detail.id)}
                  className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg border dark:border-gray-600 cursor-pointer"
                >
                  {detail.enabled ? (
                    <><ToggleRight className="w-5 h-5 text-green-500" /> <span className="text-green-600">已启用</span></>
                  ) : (
                    <><ToggleLeft className="w-5 h-5 text-gray-400" /> <span className="text-gray-500">已禁用</span></>
                  )}
                </button>
                <button onClick={() => setDetail(null)} className="p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded cursor-pointer">
                  <X className="w-5 h-5 dark:text-gray-400" />
                </button>
              </div>
            </div>
            {/* Modal Body - SKILL.md content */}
            <div className="flex-1 overflow-y-auto p-6">
              {detailLoading ? (
                <div className="text-center py-8 text-gray-500">加载中...</div>
              ) : (
                <pre className="whitespace-pre-wrap text-sm dark:text-gray-300 font-mono leading-relaxed">
                  {detail.skill_md_content || '暂无内容'}
                </pre>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
