import { FileText } from 'lucide-react';
import type { SearchResult } from '../types';

interface SearchResultsProps {
  results: SearchResult[];
  query: string;
  loading: boolean;
  onSelectSession: (id: string) => void;
}

export function SearchResults({ results, query, loading, onSelectSession }: SearchResultsProps) {
  if (!query) return null;
  if (loading) return <div className="text-center py-8 text-sm text-gray-500 dark:text-gray-400">搜索中...</div>;
  if (results.length === 0) return <div className="text-center py-8 text-sm text-gray-500 dark:text-gray-400">没有找到匹配的会话</div>;

  const highlightText = (text: string, q: string) => {
    if (!q) return text;
    const parts = text.split(new RegExp(`(${q.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi'));
    return parts.map((part, i) =>
      part.toLowerCase() === q.toLowerCase()
        ? <mark key={i} className="bg-yellow-200 dark:bg-yellow-800 px-0.5 rounded">{part}</mark>
        : part
    );
  };

  return (
    <div className="space-y-1">
      <p className="text-xs text-gray-500 dark:text-gray-400 mb-3">找到 {results.length} 个会话</p>
      {results.map(result => (
        <button
          key={result.message_id}
          onClick={() => onSelectSession(result.session_id)}
          className="w-full text-left p-3 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-800 transition-colors flex items-start gap-3"
        >
          <FileText className="w-4 h-4 text-blue-500 mt-0.5 flex-shrink-0" />
          <div className="min-w-0">
            <p className="text-sm font-medium text-gray-900 dark:text-gray-100 truncate">
              {highlightText(result.session_title || '无标题', query)}
            </p>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2">
              {highlightText(result.snippet, query)}
            </p>
          </div>
        </button>
      ))}
    </div>
  );
}
