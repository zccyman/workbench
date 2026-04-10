import { useState, useCallback } from 'react';
import { chatRecordsApi } from '../../components/chat_records/api';
import {
  useSources, useConversations, useMessages, useSearch, useStats,
} from '../../components/chat_records/hooks';
import type { Platform, BackupResult, DeleteSourceResult, ChatMessage } from '../../components/chat_records/types';
import { PLATFORM_LABELS, PLATFORM_ICONS, formatBytes, formatTimeAgo } from '../../components/chat_records/types';
import {
  MessageSquare, Search, HardDrive, Trash2, AlertTriangle,
  CheckCircle, Clock, Download, RefreshCw, X, Users, BarChart3, Loader2,
  Upload,
} from 'lucide-react';

type View = 'conversations' | 'stats';

export default function ChatRecords() {
  const [platform, setPlatform] = useState<Platform>('wechat');
  const [view, setView] = useState<View>('conversations');
  const [selectedConversation, setSelectedConversation] = useState<string | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [backupStatus, setBackupStatus] = useState<'idle' | 'running' | 'success' | 'error'>('idle');
  const [backupResult, setBackupResult] = useState<BackupResult | null>(null);
  const [backupTaskId, setBackupTaskId] = useState<string | null>(null);
  const [backupProgress, setBackupProgress] = useState<string>('');
  const [backupMode, setBackupMode] = useState<'incremental' | 'full'>('incremental');
  const [importStatus, setImportStatus] = useState<'idle' | 'running' | 'success' | 'error'>('idle');
  const [importProgress, setImportProgress] = useState<string>('');
  const [importRange, setImportRange] = useState<'all' | 'today' | 'week' | 'month' | '3days'>('all');
  const [importedConversations, setImportedConversations] = useState<{name: string; count: number}[]>([]);
  const [deleteDialog, setDeleteDialog] = useState(false);
  const [deleteConfirm, setDeleteConfirm] = useState('');
  const [deleteStatus, setDeleteStatus] = useState<'idle' | 'running' | 'success' | 'error'>('idle');
  const [deleteResult, setDeleteResult] = useState<DeleteSourceResult | null>(null);

  const { sources, reload: reloadSources } = useSources();
  const { stats } = useStats(platform);
  const { conversations, loading: convLoading } = useConversations(platform);
  const { messages, loading: msgLoading } = useMessages(platform, selectedConversation);
  const { results: searchResults, loading: searchLoading } = useSearch(platform, searchQuery);

  const currentSource = sources.find(s => s.platform === platform);

  const handleBackup = useCallback(async (full = false) => {
    setBackupStatus('running');
    setBackupResult(null);
    setBackupProgress(full ? '全量备份...' : '增量备份...');
    try {
      const result = await chatRecordsApi.startBackup(platform, full);
      const taskId = result.message?.match(/task_id:\s*(\w+)/)?.[1] || '';
      setBackupTaskId(taskId);
      
      if (taskId) {
        let retries = 0;
        while (retries < 300) {
          await new Promise(r => setTimeout(r, 500));
          try {
            const status: any = await chatRecordsApi.getBackupStatus(taskId);
            const processed = status.processed || 0;
            const total = status.total_files || 0;
            const newCount = status.new_count || 0;
            const updatedCount = status.updated_count || 0;
            const skippedCount = status.skipped_count || 0;
            const percent = total > 0 ? Math.round((processed / total) * 100) : 0;
            
            if (processed > 0) {
              setBackupProgress(`${percent}% (新:${newCount} 更新:${updatedCount} 跳过:${skippedCount})`);
            } else {
              setBackupProgress(`${percent}%`);
            }
            
            if (status.status === 'completed') {
              setBackupResult(status.result);
              setBackupStatus('success');
              setBackupProgress('完成');
              reloadSources();
              return;
            } else if (status.status === 'failed') {
              setBackupResult(status.result);
              setBackupStatus('error');
              setBackupProgress('失败');
              return;
            }
          } catch { }
          retries++;
        }
        setBackupStatus('error');
        setBackupProgress('超时');
      }
    } catch (e: any) {
      setBackupStatus('error');
      setBackupResult({ platform, status: 'error', message: e.message } as BackupResult);
      setBackupProgress(`错误: ${e.message}`);
    }
  }, [platform, reloadSources]);

  const handleImport = useCallback(async (range: 'all' | 'today' | 'week' | 'month' | '3days' = 'all') => {
    setImportStatus('running');
    setImportProgress('正在启动导入...');
    try {
      const result = await chatRecordsApi.startImport(platform, range);
      const taskId = result.task_id;
      
      if (taskId) {
        let retries = 0;
        while (retries < 300) {
          await new Promise(r => setTimeout(r, 500));
          try {
            const status: any = await chatRecordsApi.getImportStatus(taskId);
            const processed = status.processed || 0;
            const total = status.total || 0;
            const totalMessages = status.total_messages || 0;
            const percent = total > 0 ? Math.round((processed / total) * 100) : 0;
            
            if (processed > 0 && totalMessages > 0) {
              setImportProgress(`${percent}% (已导入 ${totalMessages} 条消息)`);
            } else if (processed > 0) {
              setImportProgress(`${percent}%`);
            }
            
            if (status.status === 'completed') {
              setImportStatus('success');
              const convs = status.result?.imported_conversations || [];
              setImportedConversations(convs);
              setImportProgress(`导入完成 (共 ${totalMessages} 条消息)`);
              reloadSources();
              return;
            } else if (status.status === 'failed') {
              setImportStatus('error');
              setImportProgress(`导入失败: ${status.result?.message || '未知错误'}`);
              return;
            }
          } catch { }
          retries++;
        }
        setImportStatus('error');
        setImportProgress('导入超时');
      }
    } catch (e: any) {
      setImportStatus('error');
      setImportProgress(`错误: ${e.message}`);
    }
  }, [platform, reloadSources]);

  const handleDeleteSource = useCallback(async () => {
    if (deleteConfirm !== platform) return;
    setDeleteStatus('running');
    try {
      const result = await chatRecordsApi.deleteSource(platform);
      setDeleteResult(result);
      setDeleteStatus(result.status === 'completed' ? 'success' : 'error');
      reloadSources();
    } catch (e: any) {
      setDeleteStatus('error');
      setDeleteResult({ platform, status: 'error', deleted_files: 0, failed_files: 0, freed_size: 0, errors: [e.message] } as DeleteSourceResult);
    }
    setDeleteConfirm('');
  }, [platform, deleteConfirm, reloadSources]);

  return (
    <div className="h-full flex flex-col bg-gray-50 dark:bg-gray-950">
      {/* Top Bar */}
      <header className="h-14 bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 flex items-center px-4 gap-4 flex-shrink-0">
        <h1 className="text-base font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
          <MessageSquare className="w-5 h-5 text-green-500" />
          聊天记录管理
        </h1>
        <div className="w-px h-6 bg-gray-200 dark:bg-gray-700" />
        {/* Platform Switch */}
        <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-0.5">
          {(['wechat', 'qq', 'feishu'] as Platform[]).map(p => (
            <button key={p} onClick={() => { setPlatform(p); setSelectedConversation(null); setBackupStatus('idle'); }}
              className={`px-3 py-1 rounded-md text-xs font-medium transition-all flex items-center gap-1 ${
                platform === p ? 'bg-white dark:bg-gray-700 text-blue-500 shadow-sm' : 'text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300'
              }`}>
              <span>{PLATFORM_ICONS[p]}</span> {PLATFORM_LABELS[p]}
            </button>
          ))}
        </div>
        <div className="w-px h-6 bg-gray-200 dark:bg-gray-700" />
        {/* View Switch */}
        <div className="flex bg-gray-100 dark:bg-gray-800 rounded-lg p-0.5">
          <button onClick={() => setView('conversations')}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-all flex items-center gap-1 ${
              view === 'conversations' ? 'bg-white dark:bg-gray-700 text-blue-500 shadow-sm' : 'text-gray-500 dark:text-gray-400'
            }`}>
            <MessageSquare className="w-3 h-3" /> 会话
          </button>
          <button onClick={() => setView('stats')}
            className={`px-3 py-1 rounded-md text-xs font-medium transition-all flex items-center gap-1 ${
              view === 'stats' ? 'bg-white dark:bg-gray-700 text-blue-500 shadow-sm' : 'text-gray-500 dark:text-gray-400'
            }`}>
            <BarChart3 className="w-3 h-3" /> 统计
          </button>
        </div>

        {/* Search */}
        <div className="flex-1 max-w-md mx-4 relative">
          <Search className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
          <input value={searchQuery} onChange={e => setSearchQuery(e.target.value)}
            placeholder="搜索消息..."
            className="w-full pl-9 pr-3 py-1.5 text-sm border border-gray-200 dark:border-gray-700 rounded-lg bg-gray-50 dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:border-blue-500" />
        </div>

        {/* Stats summary */}
        <div className="flex items-center gap-3 text-xs text-gray-500 dark:text-gray-400">
          <span><Users className="w-3 h-3 inline mr-1" />{stats?.total_contacts || 0} 联系人</span>
          <span><MessageSquare className="w-3 h-3 inline mr-1" />{stats?.total_messages?.toLocaleString() || 0} 消息</span>
        </div>
      </header>

      {/* Backup Bar */}
      <div className="bg-white dark:bg-gray-900 border-b border-gray-200 dark:border-gray-700 px-4 py-2 flex items-center gap-4 flex-shrink-0">
        {/* Backup Status */}
        <div className="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400">
          <HardDrive className="w-4 h-4" />
          {currentSource?.backup_exists ? (
            <>
              <CheckCircle className="w-3.5 h-3.5 text-green-500" />
              <span>已备份</span>
              <span className="text-gray-400">|</span>
              <span>{currentSource.backup_file_count} 文件</span>
              <span>{formatBytes(currentSource.backup_total_size)}</span>
              {currentSource.last_backup && (
                <span className="flex items-center gap-0.5">
                  <Clock className="w-3 h-3" />
                  {new Date(currentSource.last_backup).toLocaleString('zh-CN')}
                </span>
              )}
            </>
          ) : (
            <>
              <AlertTriangle className="w-3.5 h-3.5 text-yellow-500" />
              <span>未备份</span>
            </>
          )}
          {currentSource?.source_deleted && (
            <span className="text-red-500 flex items-center gap-0.5">
              <Trash2 className="w-3 h-3" /> 源数据已删除
            </span>
          )}
        </div>

        <div className="flex-1" />

        <div className="flex items-center gap-1 text-xs">
          <span className="text-gray-400">模式:</span>
          <select 
            value={backupMode}
            onChange={e => setBackupMode(e.target.value as 'incremental' | 'full')}
            className="bg-transparent border border-gray-300 dark:border-gray-600 rounded px-2 py-1 text-gray-700 dark:text-gray-300"
          >
            <option value="incremental">增量</option>
            <option value="full">全量</option>
          </select>
        </div>

        <button onClick={() => handleBackup(backupMode === 'full')} disabled={backupStatus === 'running'}
          className={`flex items-center gap-1.5 px-4 py-1.5 text-sm rounded-lg font-medium transition-colors ${
            backupStatus === 'running'
              ? 'bg-gray-100 dark:bg-gray-800 text-gray-500 cursor-not-allowed'
              : 'bg-blue-500 text-white hover:bg-blue-600'
          }`}>
          {backupStatus === 'running' ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>{backupProgress}</span>
            </>
          ) : (
            <>
              <Download className="w-4 h-4" />
              一键备份
            </>
          )}
        </button>

        {currentSource?.backup_exists && (
          <>
            <select
              value={importRange}
              onChange={e => setImportRange(e.target.value as any)}
              className="text-xs bg-transparent border border-gray-300 dark:border-gray-600 rounded px-2 py-1 text-gray-700 dark:text-gray-300"
            >
              <option value="all">全部</option>
              <option value="today">今天</option>
              <option value="3days">最近三天</option>
              <option value="week">最近一周</option>
              <option value="month">最近一个月</option>
            </select>
            <button onClick={() => handleImport(importRange)} disabled={importStatus === 'running'}
              className={`flex items-center gap-1.5 px-4 py-1.5 text-sm rounded-lg font-medium transition-colors ${
                importStatus === 'running'
                  ? 'bg-gray-100 dark:bg-gray-800 text-gray-500 cursor-not-allowed'
                  : 'bg-green-500 text-white hover:bg-green-600'
              }`}>
              {importStatus === 'running' ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" />
                  <span>{importProgress}</span>
                </>
              ) : (
                <>
                  <Upload className="w-4 h-4" />
                  导入聊天信息
                </>
              )}
            </button>
          </>
        )}

        {/* Delete Source Button */}
        {currentSource?.backup_exists && !currentSource?.source_deleted && (
          <button onClick={() => { setDeleteDialog(true); setDeleteConfirm(''); setDeleteStatus('idle'); }}
            className="flex items-center gap-1.5 px-4 py-1.5 text-sm rounded-lg font-medium border border-red-200 dark:border-red-800 text-red-600 dark:text-red-400 hover:bg-red-50 dark:hover:bg-red-900/20 transition-colors">
            <Trash2 className="w-4 h-4" />
            删除源数据
          </button>
        )}

        <button onClick={reloadSources} className="p-1.5 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300">
          <RefreshCw className="w-4 h-4" />
        </button>
      </div>

      {/* Backup Result */}
      {backupResult && backupStatus !== 'idle' && (
        <div className={`px-4 py-2 text-sm flex items-center gap-2 ${
          backupStatus === 'success' ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300' : 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300'
        }`}>
          {backupStatus === 'success' ? <CheckCircle className="w-4 h-4" /> : <AlertTriangle className="w-4 h-4" />}
          <span>{backupResult.message}</span>
          {backupResult.total_size > 0 && <span>({formatBytes(backupResult.total_size)})</span>}
          <button onClick={() => setBackupStatus('idle')} className="ml-auto"><X className="w-4 h-4" /></button>
        </div>
      )}

      {importStatus === 'success' && importedConversations.length > 0 && (
        <div className="px-4 py-3 bg-green-50 dark:bg-green-900/20">
          <div className="flex items-center gap-2 text-sm text-green-700 dark:text-green-300 mb-2">
            <CheckCircle className="w-4 h-4" />
            <span>导入完成 (共 {importedConversations.reduce((a, b) => a + b.count, 0)} 条消息)</span>
            <button onClick={() => { setImportStatus('idle'); setImportedConversations([]); }} className="ml-auto"><X className="w-4 h-4" /></button>
          </div>
          <div className="space-y-1">
            {importedConversations.slice(0, 10).map((conv, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
                <span className="truncate flex-1">{conv.name || '未知会话'}</span>
                <span className="ml-2 text-gray-400">{conv.count} 条</span>
              </div>
            ))}
            {importedConversations.length > 10 && (
              <div className="text-xs text-gray-400">... 还有 {importedConversations.length - 10} 个会话</div>
            )}
          </div>
        </div>
      )}

      {/* Delete Confirmation Dialog */}
      {deleteDialog && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/50">
          <div className="bg-white dark:bg-gray-900 rounded-xl shadow-2xl w-[480px] p-6">
            <h3 className="text-lg font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2 mb-4">
              <AlertTriangle className="w-5 h-5 text-red-500" />
              删除源数据
            </h3>
            <div className="space-y-3 text-sm text-gray-600 dark:text-gray-400">
              <p className="font-medium text-red-600 dark:text-red-400">
                此操作将删除 {PLATFORM_LABELS[platform]} 的原始数据文件，释放磁盘空间。删除后，{PLATFORM_LABELS[platform]} 中的聊天记录将消失。
              </p>
              <p>备份数据已保存在：{currentSource?.backup_dir}</p>
              <p>请确认已成功备份数据后再执行此操作。</p>
              <div>
                <label className="block text-xs font-medium mb-1">
                  请输入 <span className="font-mono bg-gray-100 dark:bg-gray-800 px-1 rounded">{platform}</span> 以确认删除：
                </label>
                <input value={deleteConfirm} onChange={e => setDeleteConfirm(e.target.value)}
                  className="w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-lg bg-white dark:bg-gray-800 text-gray-900 dark:text-gray-100 focus:outline-none focus:border-red-500"
                  placeholder={`输入 "${platform}" 确认`} />
              </div>
            </div>

            {deleteResult && deleteStatus !== 'idle' && (
              <div className={`mt-3 p-3 rounded-lg text-sm ${
                deleteStatus === 'success' ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-300' : 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-300'
              }`}>
                <p>删除文件：{deleteResult.deleted_files} | 失败：{deleteResult.failed_files} | 释放空间：{formatBytes(deleteResult.freed_size)}</p>
                {deleteResult.errors.length > 0 && (
                  <ul className="mt-1 text-xs list-disc list-inside">{deleteResult.errors.slice(0, 5).map((e, i) => <li key={i}>{e}</li>)}</ul>
                )}
              </div>
            )}

            <div className="flex justify-end gap-3 mt-5">
              <button onClick={() => { setDeleteDialog(false); setDeleteConfirm(''); }}
                className="px-4 py-2 text-sm rounded-lg border border-gray-300 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:bg-gray-50 dark:hover:bg-gray-800">
                取消
              </button>
              <button onClick={handleDeleteSource} disabled={deleteConfirm !== platform || deleteStatus === 'running'}
                className={`px-4 py-2 text-sm rounded-lg font-medium ${
                  deleteConfirm === platform && deleteStatus !== 'running'
                    ? 'bg-red-500 text-white hover:bg-red-600'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-500 cursor-not-allowed'
                }`}>
                {deleteStatus === 'running' ? '删除中...' : '确认删除'}
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Main Content */}
      {view === 'stats' ? (
        <div className="flex-1 overflow-auto p-6">
          <StatsPanel stats={stats} />
        </div>
      ) : searchQuery ? (
        <div className="flex-1 overflow-auto p-6">
          <SearchResults results={searchResults} loading={searchLoading} onSelect={id => setSelectedConversation(id)} />
        </div>
      ) : (
        <div className="flex flex-1 overflow-hidden">
          {/* Left: Conversations */}
          <aside className="w-80 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 flex flex-col flex-shrink-0">
            <div className="p-3 border-b border-gray-200 dark:border-gray-700">
              <p className="text-xs font-semibold text-gray-500 dark:text-gray-400 uppercase tracking-wider">
                {PLATFORM_LABELS[platform]} 会话 ({conversations.length})
              </p>
            </div>
            <div className="flex-1 overflow-auto">
              {convLoading ? (
                <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 text-blue-500 animate-spin" /></div>
              ) : conversations.length === 0 ? (
                <div className="p-6 text-center text-sm text-gray-500 dark:text-gray-400">
                  <MessageSquare className="w-10 h-10 mx-auto mb-2 opacity-30" />
                  <p>暂无会话数据</p>
                  <p className="text-xs mt-1">请先备份数据，然后执行导入</p>
                </div>
              ) : conversations.map(conv => (
                <button key={conv.id} onClick={() => setSelectedConversation(conv.id)}
                  className={`w-full text-left px-4 py-3 border-b border-gray-100 dark:border-gray-800 transition-colors ${
                    selectedConversation === conv.id ? 'bg-blue-50 dark:bg-blue-900/20' : 'hover:bg-gray-50 dark:hover:bg-gray-800'
                  }`}>
                  <div className="flex items-center justify-between">
                    <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
                      {conv.title || conv.contact_name || '未命名会话'}
                    </p>
                    {conv.last_message_time && (
                      <span className="text-xs text-gray-400 flex-shrink-0 ml-2">
                        {formatTimeAgo(conv.last_message_time)}
                      </span>
                    )}
                  </div>
                  {conv.last_message_preview && (
                    <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 truncate">{conv.last_message_preview}</p>
                  )}
                  <div className="flex items-center gap-2 mt-1">
                    <span className="text-xs text-gray-400">{conv.message_count || 0} 条消息</span>
                  </div>
                </button>
              ))}
            </div>
          </aside>

          {/* Right: Messages */}
          <main className="flex-1 flex flex-col overflow-hidden">
            {selectedConversation ? (
              <>
                <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 flex-shrink-0">
                  <h2 className="text-base font-semibold text-gray-900 dark:text-gray-100">
                    {conversations.find(c => c.id === selectedConversation)?.title || '会话'}
                  </h2>
                  <p className="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
                    {messages.length} 条消息
                  </p>
                </div>
                <div className="flex-1 overflow-auto p-4 space-y-3">
                  {msgLoading ? (
                    <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 text-blue-500 animate-spin" /></div>
                  ) : messages.map((msg) => (
                    <MessageBubble key={msg.id} message={msg} />
                  ))}
                </div>
              </>
            ) : (
              <div className="flex-1 flex flex-col items-center justify-center text-gray-500 dark:text-gray-400">
                <MessageSquare className="w-12 h-12 mb-3 opacity-30" />
                <p className="text-sm">选择一个会话查看聊天记录</p>
              </div>
            )}
          </main>
        </div>
      )}
    </div>
  );
}

function MessageBubble({ message }: { message: ChatMessage }) {
  const isSystem = message.msg_type === 'system';
  const content = message.content || '';

  if (isSystem) {
    return (
      <div className="text-center text-xs text-gray-400 py-2">
        <span className="bg-gray-100 dark:bg-gray-800 px-3 py-1 rounded-full">{content}</span>
      </div>
    );
  }

  return (
    <div className="flex gap-3 max-w-2xl">
      <div className="w-8 h-8 rounded-full bg-gray-200 dark:bg-gray-700 flex items-center justify-center text-xs font-medium text-gray-600 dark:text-gray-300 flex-shrink-0">
        {(message.sender_name || '?')[0]}
      </div>
      <div className="min-w-0 flex-1">
        <div className="flex items-center gap-2 mb-0.5">
          <span className="text-xs font-medium text-gray-700 dark:text-gray-300">{message.sender_name || '未知'}</span>
          <span className="text-xs text-gray-400">
            {message.timestamp ? new Date(message.timestamp).toLocaleString('zh-CN') : ''}
          </span>
        </div>
        <div className="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm text-gray-900 dark:text-gray-100 whitespace-pre-wrap break-words">
          {content}
        </div>
      </div>
    </div>
  );
}

function SearchResults({ results, loading, onSelect }: { results: any[]; loading: boolean; onSelect: (id: string) => void }) {
  if (loading) return <div className="flex justify-center py-12"><Loader2 className="w-6 h-6 text-blue-500 animate-spin" /></div>;
  if (!results.length) return <div className="text-center py-12 text-gray-500 dark:text-gray-400 text-sm">无搜索结果</div>;

  return (
    <div className="space-y-2">
      {results.map(r => (
        <button key={r.message_id} onClick={() => onSelect(r.conversation_id)}
          className="w-full text-left p-4 bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg hover:border-blue-300 dark:hover:border-blue-600 transition-colors">
          <div className="flex items-center gap-2 mb-1">
            <span className="text-xs text-gray-500">{r.sender_name || '未知'}</span>
            <span className="text-xs text-gray-400">{r.timestamp ? new Date(r.timestamp).toLocaleString('zh-CN') : ''}</span>
          </div>
          <p className="text-sm text-gray-900 dark:text-gray-100 line-clamp-3">{r.snippet}</p>
        </button>
      ))}
    </div>
  );
}

function StatsPanel({ stats }: { stats: any }) {
  if (!stats) return <div className="text-center py-12 text-gray-500">暂无统计数据</div>;

  return (
    <div className="space-y-6">
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">联系人</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.total_contacts}</p>
        </div>
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">会话</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.total_conversations}</p>
        </div>
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">消息</p>
          <p className="text-2xl font-bold text-gray-900 dark:text-gray-100">{stats.total_messages?.toLocaleString()}</p>
        </div>
      </div>
      {stats.platform_stats && (
        <div className="bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg p-4">
          <h3 className="text-sm font-semibold text-gray-900 dark:text-gray-100 mb-3">各平台数据</h3>
          <div className="space-y-2">
            {Object.entries(stats.platform_stats).map(([p, s]: [string, any]) => (
              <div key={p} className="flex items-center gap-4 text-sm">
                <span className="w-16 font-medium text-gray-700 dark:text-gray-300">
                  {PLATFORM_ICONS[p as Platform] || ''} {PLATFORM_LABELS[p as Platform] || p}
                </span>
                <span className="text-gray-500">{s.contacts} 联系人</span>
                <span className="text-gray-500">{s.conversations} 会话</span>
                <span className="text-gray-500">{s.messages?.toLocaleString()} 消息</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}
