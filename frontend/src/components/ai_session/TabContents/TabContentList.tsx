import { Copy, Check, Trash2, FileText, Clock, MessageSquare } from 'lucide-react';
import type { TabContent } from '../types';

interface TabContentListProps {
  contents: TabContent[];
  loading: boolean;
  selectedId: string | null;
  onSelect: (id: string) => void;
  onDelete: (id: string) => void;
  copiedId: string | null;
  onCopy: (content: TabContent) => void;
}

export function TabContentList({
  contents,
  loading,
  selectedId,
  onSelect,
  onDelete,
  copiedId,
  onCopy,
}: TabContentListProps) {
  const timeAgo = (ts: number): string => {
    if (!ts) return '';
    const diff = Date.now() - ts;
    if (diff < 60000) return '刚刚';
    if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
    if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`;
    const d = new Date(ts);
    return `${d.getMonth() + 1}/${d.getDate()}`;
  };

  if (loading) {
    return (
      <div className="flex justify-center py-12">
        <div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" />
      </div>
    );
  }

  if (contents.length === 0) {
    return (
      <div className="flex flex-col items-center justify-center py-12 text-gray-500 dark:text-gray-400">
        <FileText className="w-12 h-12 mb-3 opacity-30" />
        <p className="text-sm">暂无标签页内容</p>
        <p className="text-xs mt-1">使用浏览器扩展提取内容</p>
      </div>
    );
  }

  return (
    <div className="divide-y divide-gray-100 dark:divide-gray-800">
      {contents.map((content) => (
        <div
          key={content.id}
          className={`px-4 py-3 cursor-pointer transition-colors ${
            selectedId === content.id ? 'bg-blue-50 dark:bg-blue-900/20' : 'hover:bg-gray-50 dark:hover:bg-gray-800'
          }`}
          onClick={() => onSelect(content.id)}
        >
          <div className="flex items-start justify-between">
            <div className="flex-1 min-w-0">
              <p className="text-sm text-gray-900 dark:text-gray-100 truncate font-medium">
                {content.title || '无标题'}
              </p>
              <div className="flex items-center gap-3 mt-1.5">
                <span className="text-xs px-1.5 py-0.5 rounded bg-blue-50 dark:bg-blue-900/30 text-blue-600 dark:text-blue-400">
                  {content.source}
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                  <MessageSquare className="w-3 h-3" />
                  {content.message_count || 0} 条消息
                </span>
                <span className="text-xs text-gray-500 dark:text-gray-400 flex items-center gap-1">
                  <Clock className="w-3 h-3" />
                  {timeAgo(content.updated_at)}
                </span>
              </div>
            </div>
            <div className="flex items-center gap-1 ml-2">
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onCopy(content);
                }}
                className="p-1.5 rounded hover:bg-gray-100 dark:hover:bg-gray-700 text-gray-500 dark:text-gray-400 hover:text-blue-500"
                title="复制 Markdown"
              >
                {copiedId === content.id ? (
                  <Check className="w-4 h-4 text-green-500" />
                ) : (
                  <Copy className="w-4 h-4" />
                )}
              </button>
              <button
                onClick={(e) => {
                  e.stopPropagation();
                  onDelete(content.id);
                }}
                className="p-1.5 rounded hover:bg-red-50 dark:hover:bg-red-900/20 text-gray-500 dark:text-gray-400 hover:text-red-500"
                title="删除"
              >
                <Trash2 className="w-4 h-4" />
              </button>
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}
