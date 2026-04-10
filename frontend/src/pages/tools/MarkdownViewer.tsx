import { useState, useEffect, useCallback } from 'react';
import ReactMarkdown from 'react-markdown';
import remarkGfm from 'remark-gfm';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';
import { Prism as SyntaxHighlighter } from 'react-syntax-highlighter';
import { oneDark } from 'react-syntax-highlighter/dist/esm/styles/prism';
import api from '../../utils/api';

// KaTeX CSS
import 'katex/dist/katex.min.css';

interface DirEntry {
  name: string;
  path: string;
  type: 'directory' | 'file';
  size?: number;
  modified?: number;
}

interface FileData {
  content: string;
  path: string;
  size: number;
  modified: number;
  lines: number;
  encoding: string;
}

function formatSize(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / 1024 / 1024).toFixed(1)} MB`;
}

function formatDate(ts: number): string {
  return new Date(ts * 1000).toLocaleString('zh-CN');
}

export default function MarkdownViewer() {
  const [currentPath, setCurrentPath] = useState('/mnt/g/knowledge/wiki/topics');
  const [entries, setEntries] = useState<DirEntry[]>([]);
  const [selectedFile, setSelectedFile] = useState<FileData | null>(null);
  const [editContent, setEditContent] = useState('');
  const [mode, setMode] = useState<'view' | 'edit' | 'split'>('view');
  const [loading, setLoading] = useState(false);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchKeyword, setSearchKeyword] = useState('');
  const [searchResults, setSearchResults] = useState<any[]>([]);
  const [sidebarWidth, _setSidebarWidth] = useState(280);
  const [dark, setDark] = useState(() => document.documentElement.classList.contains('dark'));

  const loadDir = useCallback(async (path: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get(`/api/tools/markdown_viewer/dir`, { params: { path } });
      setEntries(res.data.entries);
      setCurrentPath(res.data.path);
    } catch (err: any) {
      setError(err.response?.data?.detail || '加载目录失败');
      setEntries([]);
    } finally {
      setLoading(false);
    }
  }, []);

  const loadFile = async (path: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get(`/api/tools/markdown_viewer/file`, { params: { path } });
      setSelectedFile(res.data);
      setEditContent(res.data.content);
      setMode('view');
    } catch (err: any) {
      setError(err.response?.data?.detail || '加载文件失败');
    } finally {
      setLoading(false);
    }
  };

  const saveFile = async () => {
    if (!selectedFile) return;
    setSaving(true);
    try {
      await api.put(`/api/tools/markdown_viewer/file`, {
        path: selectedFile.path,
        content: editContent,
      });
      setSelectedFile({ ...selectedFile, content: editContent });
      setError(null);
    } catch (err: any) {
      setError(err.response?.data?.detail || '保存失败');
    } finally {
      setSaving(false);
    }
  };

  const searchFiles = async () => {
    if (!searchKeyword.trim()) return;
    setLoading(true);
    try {
      const res = await api.get(`/api/tools/markdown_viewer/search`, {
        params: { path: currentPath, keyword: searchKeyword },
      });
      setSearchResults(res.data.results);
    } catch (err: any) {
      setError(err.response?.data?.detail || '搜索失败');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => { loadDir(currentPath); }, []);

  // Breadcrumb
  const breadcrumbs = currentPath.split('/').filter(Boolean);

  // Keyboard shortcuts
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 's') {
        e.preventDefault();
        if (mode !== 'view') saveFile();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, [mode, editContent, selectedFile]);

  return (
    <div className="flex flex-col h-full">
      {/* Top bar */}
      <div className="flex items-center gap-2 p-3 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <span className="text-lg">📝</span>
        <div className="flex-1 flex items-center gap-1 text-sm overflow-x-auto">
          <button onClick={() => loadDir('/')} className="text-blue-500 hover:underline">/</button>
          {breadcrumbs.map((part, i) => (
            <span key={i} className="flex items-center gap-1">
              <span className="text-gray-400">/</span>
              <button
                onClick={() => loadDir('/' + breadcrumbs.slice(0, i + 1).join('/'))}
                className="text-blue-500 hover:underline whitespace-nowrap"
              >
                {part}
              </button>
            </span>
          ))}
        </div>
        {/* Search */}
        <div className="flex items-center gap-1">
          <input
            type="text"
            value={searchKeyword}
            onChange={(e) => setSearchKeyword(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && searchFiles()}
            placeholder="搜索内容..."
            className="px-2 py-1 text-sm border rounded dark:bg-gray-700 dark:border-gray-600 w-40"
          />
          <button onClick={searchFiles} className="px-2 py-1 text-sm bg-blue-500 text-white rounded hover:bg-blue-600">
            🔍
          </button>
        </div>
        {/* Mode toggle */}
        {selectedFile && (
          <div className="flex rounded overflow-hidden border dark:border-gray-600">
            {(['view', 'edit', 'split'] as const).map((m) => (
              <button
                key={m}
                onClick={() => setMode(m)}
                className={`px-3 py-1 text-xs ${mode === m ? 'bg-blue-500 text-white' : 'bg-gray-100 dark:bg-gray-700'}`}
              >
                {m === 'view' ? '👁️ 预览' : m === 'edit' ? '✏️ 编辑' : '⬅️➡️ 分栏'}
              </button>
            ))}
          </div>
        )}
        <button onClick={() => setDark(!dark)} className="p-1 rounded hover:bg-gray-200 dark:hover:bg-gray-700">
          {dark ? '☀️' : '🌙'}
        </button>
      </div>

      {/* Search results */}
      {searchResults.length > 0 && (
        <div className="p-2 bg-yellow-50 dark:bg-yellow-900/20 border-b text-sm max-h-40 overflow-y-auto">
          <div className="flex justify-between mb-1">
            <span className="font-medium">搜索结果: {searchResults.length} 个文件</span>
            <button onClick={() => setSearchResults([])} className="text-gray-500 hover:text-red-500">✕ 关闭</button>
          </div>
          {searchResults.map((r, i) => (
            <div key={i} className="py-1 cursor-pointer hover:bg-blue-50 dark:hover:bg-blue-900/20 px-2 rounded" onClick={() => { loadFile(r.path); setSearchResults([]); }}>
              <span className="text-blue-500">{r.name}</span>
              <span className="text-gray-400 ml-2">{r.path}</span>
              {r.matches?.[0] && <div className="text-gray-500 text-xs ml-4">行{r.matches[0].line}: {r.matches[0].text}</div>}
            </div>
          ))}
        </div>
      )}

      {/* Main content */}
      <div className="flex flex-1 overflow-hidden">
        {/* Sidebar - File tree */}
        <div className="border-r border-gray-200 dark:border-gray-700 overflow-y-auto bg-gray-50 dark:bg-gray-900" style={{ width: sidebarWidth }}>
          <div className="p-2">
            <button onClick={() => {
              const parent = currentPath.split('/').slice(0, -1).join('/') || '/';
              loadDir(parent);
            }} className="text-sm text-blue-500 hover:underline mb-2 block">
              📁 ..
            </button>
            {loading && !entries.length ? (
              <div className="text-center py-8 text-gray-400">加载中...</div>
            ) : (
              entries.map((entry, i) => (
                <div
                  key={i}
                  onClick={() => entry.type === 'directory' ? loadDir(entry.path) : loadFile(entry.path)}
                  className={`flex items-center gap-2 px-2 py-1.5 rounded cursor-pointer text-sm hover:bg-blue-50 dark:hover:bg-blue-900/20 ${
                    selectedFile?.path === entry.path ? 'bg-blue-100 dark:bg-blue-900/30' : ''
                  }`}
                >
                  <span>{entry.type === 'directory' ? '📁' : '📄'}</span>
                  <span className="flex-1 truncate">{entry.name}</span>
                  {entry.type === 'file' && entry.size && (
                    <span className="text-xs text-gray-400">{formatSize(entry.size)}</span>
                  )}
                </div>
              ))
            )}
            {!loading && entries.filter(e => e.type === 'file').length === 0 && entries.filter(e => e.type === 'directory').length === 0 && (
              <div className="text-center py-8 text-gray-400 text-sm">空目录</div>
            )}
          </div>
        </div>

        {/* Content area */}
        <div className="flex-1 flex overflow-hidden">
          {error && (
            <div className="absolute top-20 right-4 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 px-4 py-2 rounded shadow-lg z-50">
              {error}
              <button onClick={() => setError(null)} className="ml-2">✕</button>
            </div>
          )}

          {!selectedFile ? (
            <div className="flex-1 flex items-center justify-center text-gray-400">
              <div className="text-center">
                <div className="text-6xl mb-4">📄</div>
                <p className="text-lg">选择一个 Markdown 文件开始查看</p>
                <p className="text-sm mt-2">共 {entries.filter(e => e.type === 'file').length} 个 .md 文件</p>
              </div>
            </div>
          ) : mode === 'view' ? (
            /* View mode */
            <div className={`flex-1 overflow-y-auto p-6 ${dark ? 'bg-white text-gray-900' : 'bg-white text-gray-900'}`}>
              <div className="max-w-4xl mx-auto prose prose-lg dark:prose-invert max-w-none
                prose-headings:font-bold prose-h1:text-3xl prose-h2:text-2xl prose-h3:text-xl
                prose-a:text-blue-500 prose-code:text-pink-500 prose-code:before:content-[''] prose-code:after:content-['']
                prose-pre:bg-gray-900 prose-pre:text-gray-100
                prose-table:border-collapse prose-th:border prose-th:border-gray-300 prose-th:px-3 prose-th:py-2
                prose-td:border prose-td:border-gray-300 prose-td:px-3 prose-td:py-2
                prose-img:rounded-lg prose-blockquote:border-l-4 prose-blockquote:border-blue-400
              ">
                <ReactMarkdown
                  remarkPlugins={[remarkGfm, remarkMath]}
                  rehypePlugins={[rehypeKatex as any]}
                  components={{
                    code({ node, inline, className, children, ...props }: any) {
                      const match = /language-(\w+)/.exec(className || '');
                      const lang = match ? match[1] : '';
                      if (!inline && (lang || String(children).includes('\n'))) {
                        return (
                          <SyntaxHighlighter
                            style={oneDark}
                            language={lang || 'text'}
                            PreTag="div"
                            className="rounded-lg !text-sm"
                            {...props}
                          >
                            {String(children).replace(/\n$/, '')}
                          </SyntaxHighlighter>
                        );
                      }
                      return <code className={className} {...props}>{children}</code>;
                    },
                  }}
                >
                  {selectedFile.content}
                </ReactMarkdown>
              </div>
            </div>
          ) : mode === 'edit' ? (
            /* Edit mode */
            <div className="flex-1 flex flex-col">
              <textarea
                value={editContent}
                onChange={(e) => setEditContent(e.target.value)}
                className="flex-1 p-4 font-mono text-sm bg-gray-900 text-green-400 resize-none outline-none"
                spellCheck={false}
              />
              <div className="flex items-center gap-2 p-2 bg-gray-100 dark:bg-gray-800 border-t">
                <button
                  onClick={saveFile}
                  disabled={saving}
                  className="px-4 py-1.5 bg-blue-500 text-white rounded hover:bg-blue-600 disabled:opacity-50 text-sm"
                >
                  {saving ? '保存中...' : '💾 保存 (Ctrl+S)'}
                </button>
                <span className="text-xs text-gray-500">
                  {editContent.length} 字符 | {editContent.split('\n').length} 行
                </span>
              </div>
            </div>
          ) : (
            /* Split mode */
            <div className="flex-1 flex">
              <div className="w-1/2 flex flex-col border-r">
                <div className="px-3 py-1 text-xs text-gray-400 bg-gray-50 dark:bg-gray-800 border-b">编辑</div>
                <textarea
                  value={editContent}
                  onChange={(e) => setEditContent(e.target.value)}
                  className="flex-1 p-4 font-mono text-sm bg-gray-900 text-green-400 resize-none outline-none"
                  spellCheck={false}
                />
              </div>
              <div className="w-1/2 flex flex-col">
                <div className="px-3 py-1 text-xs text-gray-400 bg-gray-50 dark:bg-gray-800 border-b flex justify-between">
                  <span>预览</span>
                  <button onClick={saveFile} disabled={saving} className="text-blue-500 hover:underline text-xs">
                    {saving ? '保存中...' : '💾 Ctrl+S'}
                  </button>
                </div>
                <div className="flex-1 overflow-y-auto p-6">
                  <div className="max-w-3xl mx-auto prose prose-lg dark:prose-invert max-w-none
                    prose-headings:font-bold prose-a:text-blue-500 prose-code:text-pink-500
                    prose-pre:bg-gray-900 prose-pre:text-gray-100
                    prose-table:border-collapse prose-th:border prose-th:border-gray-300
                    prose-td:border prose-td:border-gray-300
                  ">
                    <ReactMarkdown
                      remarkPlugins={[remarkGfm, remarkMath]}
                      rehypePlugins={[rehypeKatex as any]}
                      components={{
                        code({ node, inline, className, children, ...props }: any) {
                          const match = /language-(\w+)/.exec(className || '');
                          if (!inline && match) {
                            return (
                              <SyntaxHighlighter style={oneDark} language={match[1]} PreTag="div" {...props}>
                                {String(children).replace(/\n$/, '')}
                              </SyntaxHighlighter>
                            );
                          }
                          return <code className={className} {...props}>{children}</code>;
                        },
                      }}
                    >
                      {editContent}
                    </ReactMarkdown>
                  </div>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Status bar */}
      <div className="flex items-center justify-between px-3 py-1 text-xs text-gray-500 bg-gray-100 dark:bg-gray-800 border-t dark:border-gray-700">
        <div className="flex gap-4">
          {selectedFile ? (
            <>
              <span>📄 {selectedFile.path.split('/').pop()}</span>
              <span>{formatSize(selectedFile.size)}</span>
              <span>{selectedFile.lines} 行</span>
              <span>{selectedFile.encoding}</span>
              <span>修改: {formatDate(selectedFile.modified)}</span>
            </>
          ) : (
            <span>📂 {entries.filter(e => e.type === 'file').length} 个 .md 文件 | {entries.filter(e => e.type === 'directory').length} 个子目录</span>
          )}
        </div>
        <div>
          {mode !== 'view' && <span className="text-yellow-500">● 编辑中</span>}
        </div>
      </div>
    </div>
  );
}
