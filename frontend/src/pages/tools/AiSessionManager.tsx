import { useState, useMemo, useCallback, useRef, useEffect } from 'react';
import { SearchBar } from '../../components/ai_session/Search/SearchBar';
import { SearchResults } from '../../components/ai_session/Search/SearchResults';
import { MessageThread } from '../../components/ai_session/Messages/MessageThread';
import { ExportButton } from '../../components/ai_session/Export/ExportButton';
import { TabContents } from '../../components/ai_session/TabContents/TabContents';
import { KnowledgeCard } from '../../components/ai_session/Knowledge/KnowledgeCard';
import { StatsPanel } from '../../components/ai_session/Stats/StatsPanel';
import {
  useProjects, useSessions, useMessages, useSearch, useStats, useKnowledge,
} from '../../components/ai_session/hooks';
import { aiSessionApi } from '../../components/ai_session/api';
import type { DataSource } from '../../components/ai_session/types';
import {
  MessageSquare, Folder, ArrowLeft, FileText,
  CheckSquare, Square, Clock, Hash,
  BarChart3, LayoutGrid, Copy, Check, Download, FolderOpen, Globe, Lightbulb, X
} from 'lucide-react';

type TimeFilter = 'all' | 'today' | 'week' | 'month';
type SortBy = 'updated' | 'messages';
type View = 'sessions' | 'tab-contents' | 'stats';

export default function AiSessionManager() {
  const [view, setView] = useState<View>('sessions');
  const [dataSource, setDataSource] = useState<DataSource>('kilo');
  const [selectedProject, setSelectedProject] = useState<string | null>(null);
  const [selectedSession, setSelectedSession] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [timeFilter, setTimeFilter] = useState<TimeFilter>('all');
  const [sortBy, setSortBy] = useState<SortBy>('updated');
  const [selectedIds, setSelectedIds] = useState<Set<string>>(new Set());
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [showKnowledge, setShowKnowledge] = useState(false);

  const [exportDir, setExportDir] = useState('G:\\knowledge\\source\\sessions-export');
  const [exporting, setExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState<{ status: string; total: number; exported: number; failed: number } | null>(null);
  const pollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const { projects } = useProjects(dataSource);
  const { sessions, loading: sessionsLoading } = useSessions(dataSource, selectedProject ?? undefined);
  const { messages, loading: messagesLoading } = useMessages(dataSource, selectedSession);
  const { results: searchResults, loading: searchLoading } = useSearch(dataSource, searchQuery);
  const { overview, trends, projectStats, loading: statsLoading } = useStats(dataSource);
  const { items: knowledgeItems, loading: knowledgeLoading, error: knowledgeError, extract: extractKnowledge } = useKnowledge(dataSource, selectedSession);

  const filteredSessions = useMemo(() => {
    let list = [...sessions];
    const now = Date.now();
    if (timeFilter === 'today') list = list.filter(s => now - (s.time_updated || s.time_created) < 86400000);
    else if (timeFilter === 'week') list = list.filter(s => now - (s.time_updated || s.time_created) < 604800000);
    else if (timeFilter === 'month') list = list.filter(s => now - (s.time_updated || s.time_created) < 2592000000);
    if (sortBy === 'messages') list.sort((a, b) => (b.message_count || 0) - (a.message_count || 0));
    return list;
  }, [sessions, timeFilter, sortBy]);

  const toggleSelect = useCallback((id: string) => {
    setSelectedIds(prev => { const n = new Set(prev); n.has(id) ? n.delete(id) : n.add(id); return n; });
  }, []);

  const toggleAll = useCallback(() => {
    setSelectedIds(selectedIds.size === filteredSessions.length && filteredSessions.length > 0 ? new Set() : new Set(filteredSessions.map(s => s.id)));
  }, [selectedIds.size, filteredSessions]);

  const exportMarkdown = useCallback(async (sessionIds: string[]) => {
    for (const id of sessionIds) {
      try { await aiSessionApi.exportMarkdown(id, dataSource); } catch (e) { console.error('Export failed:', id, e); }
    }
  }, [dataSource]);

  const copySessionMarkdown = useCallback(async (sessionId: string) => {
    try {
      const md = await aiSessionApi.getSessionMarkdown(sessionId, dataSource);
      await navigator.clipboard.writeText(md);
      setCopiedId(sessionId);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (e) { console.error('Copy failed:', e); }
  }, [dataSource]);

  const copySelectedMarkdown = useCallback(async () => {
    try {
      let md = '';
      for (const id of selectedIds) {
        const s = sessions.find(s => s.id === id);
        md += `# ${s?.title || 'Untitled'}\n\n`;
        md += await aiSessionApi.getSessionMarkdown(id, dataSource);
        md += '\n---\n\n';
      }
      await navigator.clipboard.writeText(md);
      setCopiedId('__batch__');
      setTimeout(() => setCopiedId(null), 2000);
    } catch (e) { console.error('Batch copy failed:', e); }
  }, [selectedIds, sessions, dataSource]);

  const startExportToDir = useCallback(async () => {
    try {
      setExporting(true);
      setExportProgress(null);
      const res = await aiSessionApi.startExportToDirectory(exportDir, dataSource);
      pollRef.current = setInterval(async () => {
        try {
          const p = await aiSessionApi.getExportProgress(res.task_id);
          setExportProgress({ status: p.status, total: p.total, exported: p.exported, failed: p.failed });
          if (p.status === 'completed' || p.status === 'failed') {
            if (pollRef.current) clearInterval(pollRef.current);
            setExporting(false);
          }
        } catch {
          if (pollRef.current) clearInterval(pollRef.current);
          setExporting(false);
        }
      }, 1000);
    } catch (e) {
      console.error('Export start failed:', e);
      setExporting(false);
    }
  }, [exportDir, dataSource]);

  useEffect(() => {
    return () => {
      if (pollRef.current) clearInterval(pollRef.current);
    };
  }, []);

  const sessionObj = sessions.find(s => s.id === selectedSession);

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-950">
      {/* Top Bar */}
      <header className="h-14 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 flex items-center px-4 gap-4 flex-shrink-0">
        <h1 className="text-base font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-blue-500" />
          AI Session Manager
        </h1>
        <div className="w-px h-6 bg-gray-200 dark:bg-gray-700" />
        <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-0.5">
          <button onClick={() => setView('sessions')}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-all flex items-center gap-1 ${
              view === 'sessions' ? 'bg-white dark:bg-gray-700 text-blue-500 shadow-sm' : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
            }`}>
            <MessageSquare className="w-3 h-3" /> 会话
          </button>
          <button onClick={() => setView('tab-contents')}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-all flex items-center gap-1 ${
              view === 'tab-contents' ? 'bg-white dark:bg-gray-700 text-blue-500 shadow-sm' : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
            }`}>
            <Globe className="w-3 h-3" /> 标签页
          </button>
          <button onClick={() => setView('stats')}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-all flex items-center gap-1 ${
              view === 'stats' ? 'bg-white dark:bg-gray-700 text-blue-500 shadow-sm' : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
            }`}>
            <BarChart3 className="w-3 h-3" /> 统计
          </button>
        </div>
        {view === 'sessions' && (
          <>
            <div className="w-px h-6 bg-gray-200 dark:bg-gray-700" />
            <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-0.5">
              {(['kilo', 'opencode'] as DataSource[]).map(src => (
                <button key={src} onClick={() => setDataSource(src)}
                  className={`px-3 py-1 rounded-md text-xs font-medium transition-all ${
                    dataSource === src ? 'bg-white dark:bg-gray-700 text-blue-500 shadow-sm' : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
                  }`}>
                  {src === 'kilo' ? 'Kilo Code' : 'OpenCode'}
                </button>
              ))}
            </div>
          </>
        )}
        <div className="flex-1 max-w-md mx-4">
          <SearchBar value={searchQuery} onChange={setSearchQuery} />
        </div>
        {view === 'sessions' && (
          <div className="flex items-center gap-4 text-xs text-gray-500 dark:text-gray-400">
            <span className="flex items-center gap-1"><Hash className="w-3 h-3" />{overview?.total_sessions || 0} sessions</span>
            <span className="flex items-center gap-1"><MessageSquare className="w-3 h-3" />{overview?.total_messages?.toLocaleString() || 0} msgs</span>
            <span className="flex items-center gap-1"><Folder className="w-3 h-3" />{overview?.total_projects || 0} projects</span>
          </div>
        )}
      </header>

      {/* Main */}
      {view === 'tab-contents' ? (
        <TabContents />
      ) : view === 'stats' ? (
        <div className="flex-1 overflow-auto p-6">
          <StatsPanel overview={overview} trends={trends} projectStats={projectStats} loading={statsLoading} />
        </div>
      ) : searchQuery ? (
        <div className="flex-1 overflow-auto p-6">
          <SearchResults results={searchResults} query={searchQuery} loading={searchLoading} onSelectSession={setSelectedSession} />
        </div>
      ) : (
        <div className="flex flex-1 overflow-hidden">
          {/* Left: Projects */}
          <aside className="w-52 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 flex flex-col flex-shrink-0">
            <div className="p-3 border-b border-gray-200 dark:border-gray-700">
              <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">Projects</p>
            </div>
            <div className="flex-1 overflow-auto py-1">
              <button onClick={() => setSelectedProject(null)}
                className={`w-full text-left px-4 py-2 text-sm flex items-center gap-2 ${
                  selectedProject === null ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-500' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800'
                }`}>
                <LayoutGrid className="w-3.5 h-3.5" /> All
              </button>
              {projects.filter(p => p.name && p.name !== 'Unknown').map(project => (
                <button key={project.id} onClick={() => setSelectedProject(project.id)}
                  className={`w-full text-left px-4 py-2 text-sm flex items-center gap-2 ${
                    selectedProject === project.id ? 'bg-blue-50 dark:bg-blue-900/20 text-blue-500' : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800'
                  }`}>
                  <Folder className="w-3.5 h-3.5 flex-shrink-0" />
                  <span className="truncate flex-1">{project.name}</span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">{project.session_count || 0}</span>
                </button>
              ))}
            </div>
          </aside>

          {/* Middle: Session List */}
          <section className="w-96 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 flex flex-col flex-shrink-0">
            <div className="p-3 border-b border-gray-200 dark:border-gray-700 space-y-2">
              {/* Row 1: select + actions */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-1">
                  <button onClick={toggleAll} className="p-1 text-gray-500 dark:text-gray-400 hover:text-blue-500">
                    {selectedIds.size === filteredSessions.length && filteredSessions.length > 0
                      ? <CheckSquare className="w-4 h-4 text-blue-500" />
                      : <Square className="w-4 h-4" />}
                  </button>
                  <span className="text-xs text-gray-500 dark:text-gray-400">{filteredSessions.length} sessions</span>
                </div>
                {selectedIds.size > 0 && (
                  <div className="flex gap-1.5">
                    <button onClick={copySelectedMarkdown}
                      className="flex items-center gap-1 px-2 py-1 text-xs rounded-md border border-gray-200 dark:border-gray-700 text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800">
                      {copiedId === '__batch__' ? <Check className="w-3 h-3 text-green-500" /> : <Copy className="w-3 h-3" />}
                      复制 ({selectedIds.size})
                    </button>
                    <ExportButton label="导出选中" count={selectedIds.size} onExport={() => exportMarkdown([...selectedIds])} />
                  </div>
                )}
              </div>
              {/* Row 2: filters + sort */}
              <div className="flex items-center gap-2">
                <div className="flex bg-gray-100 dark:bg-gray-800 rounded-md p-0.5">
                  {([['all', '全部'], ['today', '今天'], ['week', '7天'], ['month', '30天']] as [TimeFilter, string][]).map(([k, v]) => (
                    <button key={k} onClick={() => setTimeFilter(k)}
                      className={`px-2 py-0.5 rounded text-xs ${timeFilter === k ? 'bg-white dark:bg-gray-700 text-blue-500 shadow-sm' : 'text-gray-500 dark:text-gray-400'}`}>{v}</button>
                  ))}
                </div>
                <select value={sortBy} onChange={e => setSortBy(e.target.value as SortBy)}
                  className="text-xs border border-gray-200 dark:border-gray-700 rounded px-1.5 py-0.5 text-gray-600 dark:text-gray-400 bg-white dark:bg-gray-800">
                  <option value="updated">最新更新</option>
                  <option value="messages">消息数</option>
                </select>
              </div>
              {/* Row 3: Export to directory */}
              <div className="flex items-center gap-2 pt-1 border-t border-gray-100 dark:border-gray-800">
                <FolderOpen className="w-3.5 h-3.5 text-gray-500 dark:text-gray-400 flex-shrink-0" />
                <input
                  type="text"
                  value={exportDir}
                  onChange={e => setExportDir(e.target.value)}
                  placeholder="导出目录路径"
                  className="flex-1 text-xs border border-gray-200 dark:border-gray-700 rounded px-2 py-1 text-gray-900 dark:text-gray-100 placeholder-gray-500 dark:placeholder-gray-400 focus:outline-none focus:border-blue-500 dark:bg-gray-800"
                  disabled={exporting}
                />
                <button
                  onClick={startExportToDir}
                  disabled={exporting}
                  className={`flex items-center gap-1 px-3 py-1 text-xs rounded-md font-medium transition-colors ${
                    exporting
                      ? 'bg-gray-100 dark:bg-gray-800 text-gray-500 dark:text-gray-400 cursor-not-allowed'
                      : 'bg-blue-500 text-white hover:bg-blue-600'
                  }`}>
                  <Download className="w-3 h-3" />
                  {exporting ? '导出中...' : '一键导出全部'}
                </button>
              </div>
              {/* Export progress */}
              {exportProgress && (
                <div className="text-xs space-y-1">
                  {exportProgress.status === 'running' && (
                    <div className="flex items-center gap-2">
                      <div className="flex-1 bg-gray-100 dark:bg-gray-800 rounded-full h-1.5 overflow-hidden">
                        <div className="bg-blue-500 h-full rounded-full transition-all"
                          style={{ width: `${exportProgress.total > 0 ? (exportProgress.exported / exportProgress.total * 100) : 0}%` }} />
                      </div>
                      <span className="text-gray-500 dark:text-gray-400">{exportProgress.exported}/{exportProgress.total}</span>
                    </div>
                  )}
                  {exportProgress.status === 'completed' && (
                    <div className="flex items-center gap-1 text-green-600 dark:text-green-400">
                      <Check className="w-3 h-3" />
                      导出完成！成功 {exportProgress.exported} 条{exportProgress.failed > 0 ? `，失败 ${exportProgress.failed} 条` : ''}
                    </div>
                  )}
                  {exportProgress.status === 'failed' && (
                    <span className="text-red-500">导出失败，请检查目录路径是否正确</span>
                  )}
                </div>
              )}
            </div>

            {/* Session list */}
            <div className="flex-1 overflow-auto">
              {sessionsLoading ? (
                <div className="flex justify-center py-12"><div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" /></div>
              ) : filteredSessions.map((session, index) => (
                <div key={session.id}
                  className={`px-3 py-3 border-b border-gray-100 dark:border-gray-800 cursor-pointer transition-colors flex items-start gap-2 ${
                    selectedSession === session.id ? 'bg-blue-50 dark:bg-blue-900/20' : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                  }`}>
                  <button onClick={e => { e.stopPropagation(); toggleSelect(session.id); }} className="mt-1 flex-shrink-0">
                    {selectedIds.has(session.id)
                      ? <CheckSquare className="w-4 h-4 text-blue-500" />
                      : <Square className="w-4 h-4 text-gray-300 dark:text-gray-600 hover:text-gray-500 dark:hover:text-gray-400" />}
                  </button>
                  <span className="mt-1 text-xs text-gray-500 dark:text-gray-400 w-6 text-right flex-shrink-0">{index + 1}</span>
                  <button onClick={() => setSelectedSession(session.id)} className="text-left flex-1 min-w-0">
                    <p className="text-sm text-gray-900 dark:text-gray-100 truncate font-medium">{session.title || '无标题'}</p>
                    <div className="flex items-center gap-2 mt-1">
                      {session.project_name && (
                        <span className="text-xs px-1.5 py-0.5 rounded bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400">{session.project_name}</span>
                      )}
                      <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-0.5">
                        <Clock className="w-3 h-3" />{timeAgo(session.time_updated || session.time_created)}
                      </span>
                      <span className="text-xs text-gray-500 dark:text-gray-400">{session.message_count || 0} msgs</span>
                    </div>
                  </button>
                </div>
              ))}
            </div>
          </section>

          {/* Right: Preview */}
          <main className="flex-1 flex flex-col overflow-hidden">
            {selectedSession && sessionObj ? (
              <>
                <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 flex items-center justify-between flex-shrink-0">
                  <div className="min-w-0 flex-1">
                    <button onClick={() => { setSelectedSession(null); setShowKnowledge(false); }}
                      className="text-xs text-blue-500 hover:underline flex items-center gap-1 mb-1">
                      <ArrowLeft className="w-3 h-3" /> 返回列表
                    </button>
                    <h2 className="text-base font-semibold text-gray-900 dark:text-gray-100 truncate">{sessionObj.title || '无标题'}</h2>
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{sessionObj.project_name} · {sessionObj.message_count || 0} messages</p>
                  </div>
                  <div className="flex gap-2 items-center">
                    <button onClick={() => setShowKnowledge(!showKnowledge)}
                      className={`flex items-center gap-1.5 px-3 py-1.5 border border-gray-200 dark:border-gray-700 text-sm rounded-lg transition-colors ${
                        showKnowledge
                          ? 'bg-yellow-50 dark:bg-yellow-900/20 text-yellow-600 dark:text-yellow-400 border-yellow-200 dark:border-yellow-800'
                          : 'text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800'
                      }`}>
                      <Lightbulb className="w-3.5 h-3.5" />
                      知识
                    </button>
                    <button onClick={() => copySessionMarkdown(selectedSession)}
                      className="flex items-center gap-1.5 px-3 py-1.5 border border-gray-200 dark:border-gray-700 text-sm rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800">
                      {copiedId === selectedSession ? <Check className="w-3.5 h-3.5 text-green-500" /> : <Copy className="w-3.5 h-3.5" />}
                      复制
                    </button>
                    <ExportButton label="导出" onExport={() => exportMarkdown([selectedSession])} />
                  </div>
                </div>

                {showKnowledge && (
                  <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900">
                    <div className="flex items-center justify-between mb-2">
                      <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-1">
                        <Lightbulb className="w-4 h-4 text-yellow-500" /> 知识提取
                      </h3>
                      <button onClick={() => setShowKnowledge(false)} className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
                        <X className="w-4 h-4" />
                      </button>
                    </div>
                    <KnowledgeCard
                      items={knowledgeItems}
                      loading={knowledgeLoading}
                      error={knowledgeError}
                      onExtract={extractKnowledge}
                    />
                  </div>
                )}

                <div className="flex-1 overflow-auto">
                  <MessageThread messages={messages} loading={messagesLoading} />
                </div>
              </>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-gray-500 dark:text-gray-400">
                <FileText className="w-12 h-12 mb-3 opacity-30" />
                <p className="text-sm">选择一个会话查看内容</p>
              </div>
            )}
          </main>
        </div>
      )}
    </div>
  );
}

function timeAgo(ts: number): string {
  if (!ts) return '';
  const diff = Date.now() - ts;
  if (diff < 60000) return '刚刚';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`;
  const d = new Date(ts);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}
