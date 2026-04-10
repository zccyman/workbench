import { useState, useEffect, useCallback } from 'react';
import {
  Plus as AddIcon, Trash2 as DeleteIcon,
  Sparkles as AutoIcon,
  MoreHorizontal as MoreVertIcon, ArrowUp as TopIcon,
  X as CloseIcon, Info
} from 'lucide-react';

const API_BASE = '/api/tools/core_assets';

interface Asset {
  id: number;
  name: string;
  description: string;
  category: string;
  icon: string;
  source_url: string;
  tags: string[];
  priority: number;
  auto_filled: boolean;
  created_at: string;
  updated_at: string;
}

const categoryColor: Record<string, string> = {
  '开发工具': '#2196f3', '搜索': '#ff9800', '内容': '#4caf50',
  '知识库': '#9c27b0', '系统': '#607d8b', '智能体': '#e91e63', 'general': '#757575',
};

export default function CoreAssets() {
  const [assets, setAssets] = useState<Asset[]>([]);
  const [loading, setLoading] = useState(true);
  const [addOpen, setAddOpen] = useState(false);
  const [detailOpen, setDetailOpen] = useState(false);
  const [selectedAsset, setSelectedAsset] = useState<Asset | null>(null);
  const [menuAnchor, setMenuAnchor] = useState<null | HTMLElement>(null);
  const [menuAsset, setMenuAsset] = useState<Asset | null>(null);
  const [autoPreview, setAutoPreview] = useState<any>(null);
  const [form, setForm] = useState({ name: '', description: '', category: '', icon: '💎', source_url: '', tags: '' });

  const fetchAssets = useCallback(async () => {
    try {
      const res = await fetch(`${API_BASE}/assets`);
      const data = await res.json();
      setAssets(data.assets || []);
    } catch (e) {
      console.error('Failed to fetch assets', e);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { fetchAssets(); }, [fetchAssets]);

  const handleAdd = async () => {
    const tags = form.tags.split(',').map(t => t.trim()).filter(Boolean);
    await fetch(`${API_BASE}/assets`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        name: form.name,
        description: form.description || undefined,
        category: form.category || undefined,
        icon: form.icon,
        source_url: form.source_url,
        tags: tags.length ? tags : undefined,
      }),
    });
    setAddOpen(false);
    setForm({ name: '', description: '', category: '', icon: '💎', source_url: '', tags: '' });
    setAutoPreview(null);
    fetchAssets();
  };

  const handleAutoFill = async () => {
    if (!form.name) return;
    try {
      const res = await fetch(`${API_BASE}/assets/search-wiki?query=${encodeURIComponent(form.name)}`);
      const data = await res.json();
      setAutoPreview(data);
      if (data.matches?.length > 0) {
        const snippet = data.matches[0].snippet || '';
        setForm(f => ({
          ...f,
          description: f.description || `（自动补充）${snippet.slice(0, 150)}`,
        }));
      }
    } catch (e) {
      console.error('Auto-fill failed', e);
    }
  };

  const handleRemove = async (id: number) => {
    if (!confirm('确认移除此资产？')) return;
    await fetch(`${API_BASE}/assets/${id}`, { method: 'DELETE' });
    setMenuAnchor(null);
    fetchAssets();
  };

  const handleTop = async (id: number) => {
    const ids = [id, ...assets.filter(a => a.id !== id).map(a => a.id)];
    await fetch(`${API_BASE}/assets/reorder`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(ids),
    });
    setMenuAnchor(null);
    fetchAssets();
  };

  return (
    <div className="p-6">
      <div className="flex justify-between items-center mb-4">
        <div>
          <h2 className="text-2xl font-bold">💎 核心资产</h2>
          <p className="text-gray-500 text-sm">{assets.length} 个资产 · {assets.filter(a => a.auto_filled).length} 个已自动补充</p>
        </div>
        <button className="bg-blue-600 text-white px-4 py-2 rounded flex items-center gap-2 hover:bg-blue-700" onClick={() => setAddOpen(true)}>
          <AddIcon size={18} /> 添加资产
        </button>
      </div>

      {assets.length === 0 && !loading && (
        <div className="bg-blue-50 text-blue-700 p-4 rounded mt-4 flex items-center gap-2">
          <Info size={18} /> 暂无核心资产。点击"添加资产"开始管理。
        </div>
      )}

      <div className="space-y-3">
        {assets.map((asset, idx) => (
          <div key={asset.id} className="bg-white border rounded-lg p-4 hover:shadow-md transition-shadow">
            <div className="flex justify-between items-start">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-lg font-semibold">{asset.icon} {asset.name}</span>
                  {idx === 0 && <span className="bg-blue-600 text-white text-xs px-2 py-0.5 rounded">置顶</span>}
                  {asset.auto_filled && (
                    <span className="border border-blue-500 text-blue-500 text-xs px-2 py-0.5 rounded flex items-center gap-1">
                      <AutoIcon size={12} /> 自动补充
                    </span>
                  )}
                </div>
                <p className="text-gray-500 text-sm mb-2">{asset.description || '无描述'}</p>
                <div className="flex flex-wrap gap-1">
                  <span
                    className="text-white text-xs px-2 py-0.5 rounded"
                    style={{ backgroundColor: categoryColor[asset.category] || categoryColor.general }}
                  >
                    {asset.category}
                  </span>
                  {asset.tags?.map(tag => (
                    <span key={tag} className="border border-gray-300 text-gray-600 text-xs px-2 py-0.5 rounded">{tag}</span>
                  ))}
                </div>
              </div>
              <button className="p-1 hover:bg-gray-100 rounded" onClick={(e) => { setMenuAnchor(e.currentTarget); setMenuAsset(asset); }}>
                <MoreVertIcon size={20} />
              </button>
            </div>
          </div>
        ))}
      </div>

      {/* 右键菜单 */}
      {menuAnchor && (
        <div
          className="fixed bg-white border rounded shadow-lg py-1 z-50"
          style={{ top: menuAnchor.getBoundingClientRect().top + 30, left: menuAnchor.getBoundingClientRect().left }}
        >
          <button
            className="w-full px-4 py-2 text-left hover:bg-gray-100 flex items-center gap-2"
            onClick={() => { setDetailOpen(true); setSelectedAsset(menuAsset); setMenuAnchor(null); }}
          >
            查看详情
          </button>
          <button
            className="w-full px-4 py-2 text-left hover:bg-gray-100 flex items-center gap-2"
            onClick={() => menuAsset && handleTop(menuAsset.id)}
          >
            <TopIcon size={14} /> 置顶
          </button>
          <button
            className="w-full px-4 py-2 text-left hover:bg-gray-100 flex items-center gap-2 text-red-600"
            onClick={() => menuAsset && handleRemove(menuAsset.id)}
          >
            <DeleteIcon size={14} /> 移除
          </button>
        </div>
      )}

      {/* 添加对话框 */}
      {addOpen && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setAddOpen(false)}>
          <div className="bg-white rounded-lg w-full max-w-md p-6" onClick={e => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">添加核心资产</h3>
              <button className="p-1 hover:bg-gray-100 rounded" onClick={() => setAddOpen(false)}><CloseIcon /></button>
            </div>
            <div className="space-y-4">
              <div className="flex gap-2">
                <input
                  type="text"
                  placeholder="名称 *"
                  className="border rounded px-3 py-2 flex-1"
                  value={form.name}
                  onChange={e => setForm(f => ({ ...f, name: e.target.value }))}
                />
                <button
                  className="border px-3 py-2 rounded flex items-center gap-2 hover:bg-gray-50"
                  onClick={handleAutoFill}
                  disabled={!form.name}
                >
                  <AutoIcon size={16} /> 自动补充
                </button>
              </div>
              {autoPreview && autoPreview.matches?.length > 0 && (
                <div className="bg-green-50 text-green-700 p-3 rounded flex items-center gap-2">
                  <AutoIcon size={16} /> 找到 {autoPreview.matches.length} 个知识库匹配，已自动补充描述
                </div>
              )}
              <textarea
                placeholder="描述"
                className="border rounded px-3 py-2 w-full"
                rows={2}
                value={form.description}
                onChange={e => setForm(f => ({ ...f, description: e.target.value }))}
              />
              <div className="flex gap-4">
                <input
                  type="text"
                  placeholder="分类"
                  className="border rounded px-3 py-2 flex-1"
                  value={form.category}
                  onChange={e => setForm(f => ({ ...f, category: e.target.value }))}
                />
                <input
                  type="text"
                  placeholder="图标"
                  className="border rounded px-3 py-2 w-20"
                  value={form.icon}
                  onChange={e => setForm(f => ({ ...f, icon: e.target.value }))}
                />
              </div>
              <input
                type="text"
                placeholder="来源链接"
                className="border rounded px-3 py-2 w-full"
                value={form.source_url}
                onChange={e => setForm(f => ({ ...f, source_url: e.target.value }))}
              />
              <input
                type="text"
                placeholder="标签（逗号分隔）"
                className="border rounded px-3 py-2 w-full"
                value={form.tags}
                onChange={e => setForm(f => ({ ...f, tags: e.target.value }))}
              />
            </div>
            <div className="flex justify-end gap-2 mt-6">
              <button className="px-4 py-2 border rounded hover:bg-gray-50" onClick={() => setAddOpen(false)}>取消</button>
              <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700" onClick={handleAdd} disabled={!form.name}>添加</button>
            </div>
          </div>
        </div>
      )}

      {/* 详情对话框 */}
      {detailOpen && selectedAsset && (
        <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50" onClick={() => setDetailOpen(false)}>
          <div className="bg-white rounded-lg w-full max-w-md p-6" onClick={e => e.stopPropagation()}>
            <div className="flex justify-between items-center mb-4">
              <h3 className="text-xl font-bold">{selectedAsset.icon} {selectedAsset.name}</h3>
              <button className="p-1 hover:bg-gray-100 rounded" onClick={() => setDetailOpen(false)}><CloseIcon /></button>
            </div>
            <div className="space-y-4">
              <div>
                <p className="text-gray-500 text-sm">描述</p>
                <p>{selectedAsset.description || '无'}</p>
              </div>
              <div>
                <p className="text-gray-500 text-sm">分类</p>
                <span
                  className="text-white text-xs px-2 py-0.5 rounded inline-block"
                  style={{ backgroundColor: categoryColor[selectedAsset.category] || categoryColor.general }}
                >
                  {selectedAsset.category}
                </span>
              </div>
              {selectedAsset.source_url && (
                <div>
                  <p className="text-gray-500 text-sm">来源</p>
                  <a href={selectedAsset.source_url} target="_blank" rel="noreferrer" className="text-blue-600 hover:underline">{selectedAsset.source_url}</a>
                </div>
              )}
              <div>
                <p className="text-gray-500 text-sm">标签</p>
                <div className="flex flex-wrap gap-1 mt-1">
                  {selectedAsset.tags?.map(t => (
                    <span key={t} className="border border-gray-300 text-gray-600 text-xs px-2 py-0.5 rounded">{t}</span>
                  ))}
                </div>
              </div>
              <div>
                <p className="text-gray-500 text-sm">优先级</p>
                <p>{selectedAsset.priority}</p>
              </div>
              <div>
                <p className="text-gray-500 text-sm">创建时间</p>
                <p>{new Date(selectedAsset.created_at).toLocaleString('zh-CN')}</p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}