import { useState, useCallback, useEffect, useRef } from 'react';
import { SearchBar } from '../Search/SearchBar';
import { TabContentList } from './TabContentList';
import { TabContentDetail } from './TabContentDetail';
import { aiSessionApi } from '../api';
import type { TabContent } from '../types';
import { Globe, Plus, RefreshCw, Download, Loader2 } from 'lucide-react';

const DEFAULT_EXPORT_DIR = 'G:\\knowledge\\source\\browser-export';

export function TabContents() {
  const [contents, setContents] = useState<TabContent[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);
  const [selectedContent, setSelectedContent] = useState<TabContent | null>(null);
  const [searchQuery, setSearchQuery] = useState('');
  const [loading, setLoading] = useState(true);
  const [copiedId, setCopiedId] = useState<string | null>(null);
  const [exporting, setExporting] = useState(false);
  const [exportProgress, setExportProgress] = useState<{ status: string; total: number; exported: number; failed: number; output_dir: string | null; errors: string[] } | null>(null);
  const [showExportConfig, setShowExportConfig] = useState(false);
  const [exportDir, setExportDir] = useState(DEFAULT_EXPORT_DIR);
  const exportPollRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const loadContents = useCallback(async () => {
    setLoading(true);
    try {
      const data = searchQuery
        ? await aiSessionApi.searchTabContents(searchQuery)
        : await aiSessionApi.getTabContents();
      setContents(data);
    } catch (error) {
      console.error('Failed to load tab contents:', error);
    } finally {
      setLoading(false);
    }
  }, [searchQuery]);

  useEffect(() => {
    loadContents();
  }, [loadContents]);

  useEffect(() => {
    const interval = setInterval(() => {
      loadContents();
    }, 10000);
    return () => clearInterval(interval);
  }, [loadContents]);

  useEffect(() => {
    if (selectedId) {
      aiSessionApi.getTabContent(selectedId).then(setSelectedContent).catch(console.error);
    } else {
      setSelectedContent(null);
    }
  }, [selectedId]);

  const handleCopy = useCallback(async (content: TabContent) => {
    try {
      await navigator.clipboard.writeText(content.markdown);
      setCopiedId(content.id);
      setTimeout(() => setCopiedId(null), 2000);
    } catch (error) {
      console.error('Copy failed:', error);
    }
  }, []);

  const handleDownload = useCallback((content: TabContent) => {
    const blob = new Blob([content.markdown], { type: 'text/markdown;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${(content.title || 'untitled').replace(/[<>:"/\\|?*]/g, '_')}.md`;
    a.click();
    URL.revokeObjectURL(url);
  }, []);

  const handleDelete = useCallback(async (id: string) => {
    if (!confirm('确定删除此内容？')) return;
    try {
      await aiSessionApi.deleteTabContent(id);
      setContents((prev) => prev.filter((c) => c.id !== id));
      if (selectedId === id) {
        setSelectedId(null);
        setSelectedContent(null);
      }
    } catch (error) {
      console.error('Delete failed:', error);
    }
  }, [selectedId]);

  const handleExport = useCallback(async () => {
    if (!exportDir.trim()) return;
    setExporting(true);
    setExportProgress(null);
    try {
      const { task_id } = await aiSessionApi.exportTabContentsToDirectory(exportDir.trim());
      setShowExportConfig(false);

      const poll = async () => {
        try {
          const progress = await aiSessionApi.getTabExportProgress(task_id);
          setExportProgress(progress);
          if (progress.status === 'completed' || progress.status === 'failed') {
            setExporting(false);
            if (exportPollRef.current) {
              clearInterval(exportPollRef.current);
              exportPollRef.current = null;
            }
          }
        } catch (e) {
          console.error('Poll error:', e);
        }
      };

      exportPollRef.current = window.setInterval(poll, 500);
      poll();
    } catch (error) {
      console.error('Export failed:', error);
      setExporting(false);
    }
  }, [exportDir]);

  useEffect(() => {
    return () => {
      if (exportPollRef.current) {
        clearInterval(exportPollRef.current);
      }
    };
  }, []);

  const handleAdd = useCallback(async () => {
    const markdown = prompt('粘贴 Markdown 内容：');
    if (!markdown) return;
    const title = prompt('标题：') || '导入的内容';
    try {
      const newContent = await aiSessionApi.createTabContent({ title, markdown });
      setContents((prev) => [newContent, ...prev]);
      setSelectedId(newContent.id);
    } catch (error) {
      console.error('Create failed:', error);
    }
  }, []);

  return (
    <div className="flex-1 flex flex-col bg-gray-50 dark:bg-gray-950">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-900 flex items-center gap-4">
        <h2 className="text-base font-semibold text-gray-900 dark:text-gray-100 flex items-center gap-2">
          <Globe className="w-5 h-5 text-blue-500" />
          标签页内容
        </h2>
        <div className="flex-1 max-w-md">
          <SearchBar value={searchQuery} onChange={setSearchQuery} />
        </div>
        <button
          onClick={handleAdd}
          className="flex items-center gap-1 px-3 py-1.5 bg-blue-500 text-white text-sm rounded-lg hover:bg-blue-600"
        >
          <Plus className="w-4 h-4" />
          手动添加
        </button>
        <button
          onClick={() => setShowExportConfig(!showExportConfig)}
          disabled={exporting}
          className="flex items-center gap-1 px-3 py-1.5 bg-green-500 text-white text-sm rounded-lg hover:bg-green-600 disabled:opacity-50"
        >
          {exporting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
          批量导出
        </button>
        <button
          onClick={() => loadContents()}
          disabled={loading}
          className="flex items-center gap-1 px-3 py-1.5 border border-gray-200 dark:border-gray-700 text-sm rounded-lg text-gray-600 dark:text-gray-400 hover:bg-gray-50 dark:hover:bg-gray-800 disabled:opacity-50"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          刷新
        </button>
      </div>

      {showExportConfig && (
        <div className="p-3 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900 flex items-center gap-3">
          <label className="text-sm text-gray-600 dark:text-gray-400 whitespace-nowrap">导出目录：</label>
          <input
            type="text"
            value={exportDir}
            onChange={(e) => setExportDir(e.target.value)}
            className="flex-1 px-3 py-1.5 border border-gray-200 dark:border-gray-700 rounded-lg text-sm focus:outline-none focus:border-blue-500 dark:bg-gray-800 dark:text-gray-100"
            placeholder="G:\knowledge\source\browser-export"
          />
          <button
            onClick={handleExport}
            disabled={exporting || !exportDir.trim()}
            className="flex items-center gap-1 px-4 py-1.5 bg-green-500 text-white text-sm rounded-lg hover:bg-green-600 disabled:opacity-50"
          >
            {exporting ? <Loader2 className="w-4 h-4 animate-spin" /> : <Download className="w-4 h-4" />}
            开始导出
          </button>
          <button
            onClick={() => setShowExportConfig(false)}
            className="text-sm text-gray-500 dark:text-gray-400 hover:text-gray-700 dark:hover:text-gray-300"
          >
            取消
          </button>
        </div>
      )}

      {exportProgress && (
        <div className={`p-3 border-b border-gray-200 dark:border-gray-700 text-sm ${exportProgress.status === 'completed' ? 'bg-green-50 dark:bg-green-900/20 text-green-700 dark:text-green-400' : exportProgress.status === 'failed' ? 'bg-red-50 dark:bg-red-900/20 text-red-700 dark:text-red-400' : 'bg-blue-50 dark:bg-blue-900/20 text-blue-700 dark:text-blue-400'}`}>
          {exportProgress.status === 'completed' ? (
            <div className="flex items-center justify-between">
              <span>导出完成：{exportProgress.exported}/{exportProgress.total} 个文件已保存到 {exportProgress.output_dir}</span>
              {exportProgress.failed > 0 && <span className="text-yellow-600 dark:text-yellow-400">（{exportProgress.failed} 个失败）</span>}
              <button onClick={() => setExportProgress(null)} className="text-xs text-gray-500 hover:text-gray-700">关闭</button>
            </div>
          ) : exportProgress.status === 'failed' ? (
            <div className="flex items-center justify-between">
              <span>导出失败：{exportProgress.errors.join(', ')}</span>
              <button onClick={() => setExportProgress(null)} className="text-xs text-gray-500 hover:text-gray-700">关闭</button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <Loader2 className="w-4 h-4 animate-spin" />
              <span>正在导出...</span>
            </div>
          )}
        </div>
      )}

      <div className="flex-1 flex overflow-hidden">
        <div className="w-80 bg-white dark:bg-gray-900 border-r border-gray-200 dark:border-gray-700 flex-shrink-0 overflow-auto">
          <TabContentList
            contents={contents}
            loading={loading}
            selectedId={selectedId}
            onSelect={setSelectedId}
            onDelete={handleDelete}
            copiedId={copiedId}
            onCopy={handleCopy}
          />
        </div>

        <div className="flex-1 flex flex-col overflow-hidden">
          <TabContentDetail
            content={selectedContent}
            onBack={() => setSelectedId(null)}
            onCopy={handleCopy}
            onDownload={handleDownload}
            copied={copiedId === selectedId}
          />
        </div>
      </div>
    </div>
  );
}
