import React from 'react';

export interface Favorite {
  id: string;
  name: string;
  windowsPath: string;
  wslPath: string;
}

interface FavoritesPanelProps {
  favorites: Favorite[];
  onSelect: (wslPath: string) => void;
  onDelete: (id: string) => void;
  onAdd: () => void;
  isOpen: boolean;
  onClose: () => void;
}

export const FavoritesPanel: React.FC<FavoritesPanelProps> = ({
  favorites,
  onSelect,
  onDelete,
  onAdd,
  isOpen,
  onClose,
}) => {
  if (!isOpen) return null;

  return (
    <div className="absolute right-0 top-full mt-2 w-80 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-700 z-50">
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
        <h3 className="font-semibold dark:text-white">收藏夹</h3>
        <button onClick={onClose} className="text-gray-500 hover:text-gray-700 dark:hover:text-gray-300">
          ✕
        </button>
      </div>
      <div className="max-h-64 overflow-y-auto">
        {favorites.length === 0 ? (
          <p className="p-4 text-gray-500 dark:text-gray-400 text-center">暂无收藏</p>
        ) : (
          <ul>
            {favorites.map((fav) => (
              <li
                key={fav.id}
                className="flex items-center justify-between p-3 hover:bg-gray-50 dark:hover:bg-gray-700"
              >
                <button
                  onClick={() => onSelect(fav.wslPath)}
                  className="flex-1 text-left dark:text-gray-200"
                >
                  <div className="font-medium">{fav.name}</div>
                  <div className="text-xs text-gray-500 dark:text-gray-400 truncate">{fav.wslPath}</div>
                </button>
                <button
                  onClick={() => onDelete(fav.id)}
                  className="text-red-500 hover:text-red-700 ml-2"
                >
                  🗑
                </button>
              </li>
            ))}
          </ul>
        )}
      </div>
      <div className="p-3 border-t border-gray-200 dark:border-gray-700">
        <button
          onClick={onAdd}
          className="w-full py-2 bg-blue-500 hover:bg-blue-600 text-white rounded-lg transition-colors"
        >
          + 添加当前路径
        </button>
      </div>
    </div>
  );
};