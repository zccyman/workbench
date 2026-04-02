import { useState, useEffect } from 'react';
import { PathInput } from '../../components/wsl/PathInput';
import { Breadcrumb } from '../../components/wsl/Breadcrumb';
import { FileList, type FileEntry } from '../../components/wsl/FileList';
import { CopyButton } from '../../components/wsl/CopyButton';
import { FavoritesPanel, type Favorite } from '../../components/wsl/FavoritesPanel';
import { windowsToWsl, wslToWindows, isWslPath } from '../utils/pathUtils';
import api from '../utils/api';

interface DirResponse {
  entries: FileEntry[];
}

export default function WslPathBridge() {
  const [currentPath, setCurrentPath] = useState('/mnt');
  const [entries, setEntries] = useState<FileEntry[]>([]);
  const [inputPath, setInputPath] = useState('/mnt');
  const [favorites, setFavorites] = useState<Favorite[]>([]);
  const [showFavorites, setShowFavorites] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchFavorites();
  }, []);

  useEffect(() => {
    loadDirectory(currentPath);
  }, [currentPath]);

  const fetchFavorites = async () => {
    try {
      const res = await api.get('/api/tools/wsl_path_bridge/favorites');
      setFavorites(res.data.favorites);
    } catch (err) {
      console.error('Failed to fetch favorites:', err);
    }
  };

  const loadDirectory = async (path: string) => {
    setLoading(true);
    setError(null);
    try {
      const res = await api.get(`/api/tools/wsl_path_bridge/dir`, { params: { path } });
      setEntries(res.data.entries);
    } catch (err) {
      setError('目录不存在或无法访问');
      setEntries([]);
    } finally {
      setLoading(false);
    }
  };

  const handleNavigate = (path: string) => {
    setCurrentPath(path);
    setInputPath(path);
  };

  const handleInputSubmit = () => {
    const targetPath = inputPath.trim();
    if (!targetPath) return;
    if (isWslPath(targetPath)) {
      setCurrentPath(targetPath);
    } else {
      const wslPath = windowsToWsl(targetPath);
      setCurrentPath(wslPath);
      setInputPath(wslPath);
    }
  };

  const refreshDirectory = () => loadDirectory(currentPath);

  const handlePathInputChange = (value: string) => {
    setInputPath(value);
    if (isWslPath(value)) setCurrentPath(value);
  };

  const handleAddFavorite = async () => {
    const windowsPath = wslToWindows(currentPath);
    const name = currentPath.split('/').pop() || '收藏';
    try {
      await api.post('/api/tools/wsl_path_bridge/favorites', { name, windowsPath, wslPath: currentPath });
      fetchFavorites();
    } catch (err) {
      console.error('Failed to add favorite:', err);
    }
  };

  const handleDeleteFavorite = async (id: string) => {
    try {
      await api.delete(`/api/tools/wsl_path_bridge/favorites/${id}`);
      fetchFavorites();
    } catch (err) {
      console.error('Failed to delete favorite:', err);
    }
  };

  const handleDelete = async (path: string, isDirectory: boolean) => {
    const type = isDirectory ? '文件夹' : '文件';
    if (!confirm(`确定要删除${type} "${path}" 吗？此操作不可撤销。`)) return;
    try {
      await api.delete('/api/tools/wsl_path_bridge/file', { params: { path } });
      refreshDirectory();
    } catch (err: any) {
      alert(err.response?.data?.detail || '删除失败');
    }
  };

  const windowsPath = wslToWindows(currentPath);

  return (
    <div>
      <h1 className="text-2xl font-bold mb-6">📂 WSL 路径转换</h1>

      <div className="mb-6">
        <PathInput value={inputPath} onChange={handlePathInputChange} onSubmit={handleInputSubmit} onRefresh={refreshDirectory} loading={loading} />
      </div>

      <div className="mb-4 p-3 rounded-lg" style={{ backgroundColor: 'var(--bg-primary)' }}>
        <Breadcrumb path={currentPath} onNavigate={handleNavigate} />
      </div>

      {error && (
        <div className="mb-4 p-4 bg-red-100 dark:bg-red-900/30 text-red-700 dark:text-red-300 rounded-lg">{error}</div>
      )}

      {loading ? (
        <div className="text-center py-8" style={{ color: 'var(--text-secondary)' }}>加载中...</div>
      ) : (
        <>
          <div className="grid grid-cols-2 gap-6 mb-6">
            <div className="border rounded-lg overflow-hidden" style={{ borderColor: 'var(--border)' }}>
              <div className="px-4 py-2 border-b font-semibold" style={{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border)' }}>Windows 路径</div>
              <div className="p-4 max-h-96 overflow-y-auto">
                <FileList entries={entries} onNavigate={(path) => handleNavigate(windowsToWsl(path))} onDelete={handleDelete} />
              </div>
            </div>
            <div className="border rounded-lg overflow-hidden" style={{ borderColor: 'var(--border)' }}>
              <div className="px-4 py-2 border-b font-semibold" style={{ backgroundColor: 'var(--bg-primary)', borderColor: 'var(--border)' }}>WSL 路径</div>
              <div className="p-4 max-h-96 overflow-y-auto">
                <FileList entries={entries} onNavigate={handleNavigate} onDelete={handleDelete} />
              </div>
            </div>
          </div>

          <div className="flex justify-center gap-4">
            <CopyButton text={windowsPath} label="复制 Windows 路径" />
            <CopyButton text={currentPath} label="复制 WSL 路径" />
          </div>
        </>
      )}
    </div>
  );
}
