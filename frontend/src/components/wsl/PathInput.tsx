import React from 'react';

interface PathInputProps {
  value: string;
  onChange: (path: string) => void;
  onSubmit: () => void;
  onRefresh: () => void;
  loading: boolean;
}

export const PathInput: React.FC<PathInputProps> = ({ value, onChange, onSubmit, onRefresh, loading }) => {
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') {
      onSubmit();
    }
  };

  return (
    <div className="w-full flex gap-2">
      <input
        type="text"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="输入路径 (例如: G:\knowledge\Project 或 /mnt/g/knowledge/Project)"
        className="flex-1 px-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500 dark:bg-gray-800 dark:border-gray-600 dark:text-white"
      />
      <button
        onClick={onRefresh}
        disabled={loading}
        className="px-4 py-2 border rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 dark:border-gray-600 dark:text-white transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <svg
          className={`w-5 h-5 ${loading ? 'animate-spin' : ''}`}
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
          />
        </svg>
      </button>
    </div>
  );
};