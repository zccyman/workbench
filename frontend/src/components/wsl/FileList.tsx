import React from 'react';

export interface FileEntry {
  name: string;
  isDirectory: boolean;
  path: string;
}

interface FileListProps {
  entries: FileEntry[];
  onNavigate: (path: string) => void;
  onDelete?: (path: string, isDirectory: boolean) => void;
}

export const FileList: React.FC<FileListProps> = ({ entries, onNavigate, onDelete }) => {
  if (entries.length === 0) {
    return (
      <div className="text-center text-gray-500 dark:text-gray-400 py-8">
        空目录
      </div>
    );
  }

  return (
    <div className="space-y-1 group">
      {entries.map((entry) => (
        <div
          key={entry.path}
          onClick={() => entry.isDirectory && onNavigate(entry.path)}
          className={`flex items-center justify-between gap-2 px-3 py-2 rounded cursor-pointer transition-colors ${
            entry.isDirectory
              ? 'hover:bg-blue-50 dark:hover:bg-blue-900/30 cursor-pointer'
              : 'cursor-default'
          }`}
        >
          <div className="flex items-center gap-2 flex-1 min-w-0">
            <span className="text-lg">
              {entry.isDirectory ? '📁' : '📄'}
            </span>
            <span className={`dark:text-gray-200 ${!entry.isDirectory && 'text-gray-500 dark:text-gray-400'} truncate`}>
              {entry.name}
            </span>
          </div>
          {onDelete && (
            <button
              onClick={(e) => {
                e.stopPropagation();
                onDelete(entry.path, entry.isDirectory);
              }}
              className="p-1 text-gray-400 hover:text-red-500 dark:hover:text-red-400 opacity-0 group-hover:opacity-100 transition-opacity"
              title="删除"
            >
              🗑️
            </button>
          )}
        </div>
      ))}
    </div>
  );
};