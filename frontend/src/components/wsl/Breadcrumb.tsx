import React from 'react';

interface BreadcrumbProps {
  path: string;
  onNavigate: (path: string) => void;
}

export const Breadcrumb: React.FC<BreadcrumbProps> = ({ path, onNavigate }) => {
  const normalized = path.replace(/\\/g, '/');
  const parts = normalized.split('/').filter(Boolean);
  const isWsl = normalized.startsWith('/mnt/');

  const buildPath = (index: number): string => {
    if (index === 0) {
      return isWsl ? '/' : parts[0] + ':\\';
    }
    const base = isWsl ? '/' + parts.slice(0, index).join('/') : parts[0] + ':\\' + parts.slice(1, index).join('\\');
    return isWsl ? base : base;
  };

  return (
    <div className="flex items-center gap-2 text-sm text-gray-600 dark:text-gray-300 overflow-x-auto">
      {isWsl ? (
        <>
          <button
            onClick={() => onNavigate('/')}
            className="hover:text-blue-500 dark:hover:text-blue-400 hover:underline"
          >
            根
          </button>
          {parts.map((part, index) => (
            <React.Fragment key={index}>
              <span className="text-gray-400">/</span>
              <button
                onClick={() => onNavigate(buildPath(index + 1))}
                className="hover:text-blue-500 dark:hover:text-blue-400 hover:underline whitespace-nowrap"
              >
                {part}
              </button>
            </React.Fragment>
          ))}
        </>
      ) : (
        <>
          <button
            onClick={() => onNavigate(parts[0] + ':\\')}
            className="hover:text-blue-500 dark:hover:text-blue-400 hover:underline"
          >
            {parts[0]}:
          </button>
          {parts.slice(1).map((part, index) => (
            <React.Fragment key={index}>
              <span className="text-gray-400">\</span>
              <button
                onClick={() => onNavigate(parts[0] + ':\\' + parts.slice(1, index + 2).join('\\'))}
                className="hover:text-blue-500 dark:hover:text-blue-400 hover:underline whitespace-nowrap"
              >
                {part}
              </button>
            </React.Fragment>
          ))}
        </>
      )}
    </div>
  );
};