import api from '../../utils/api';
import type { Platform, SourceStatus, BackupResult, DeleteSourceResult, BackupHistoryEntry, ChatContact, ChatConversation, ChatMessage, SearchResult, StatsOverview } from './types';

const BASE = '/api/tools/chat_records';

async function fetchApi<T>(endpoint: string, options?: { method?: string; body?: any }): Promise<T> {
  const config: any = { method: options?.method || 'GET' };
  if (options?.body) config.data = options.body;
  const response = await api(`${BASE}${endpoint}`, config);
  return response.data;
}

export const chatRecordsApi = {
  getSources: () => fetchApi<SourceStatus[]>('/sources'),

  executeBackup: (platform: Platform) =>
    fetchApi<BackupResult>(`/backup/${platform}/execute`, { method: 'POST' }),

  startBackup: (platform: Platform, full = false) =>
    fetchApi<BackupResult>(`/backup/${platform}?full=${full}`, { method: 'POST' }),

  getBackupStatus: (taskId: string) =>
    fetchApi<any>(`/backup/status/${taskId}`),

  getBackupHistory: (platform?: Platform) => {
    const q = platform ? `?platform=${platform}` : '';
    return fetchApi<BackupHistoryEntry[]>(`/backup/history${q}`);
  },

  deleteSource: (platform: Platform) =>
    fetchApi<DeleteSourceResult>(`/backup/${platform}/delete-source`, {
      method: 'POST',
      body: JSON.stringify({ confirm_name: platform }),
    }),

  getContacts: (platform: Platform, type?: string, limit = 200) => {
    const params = new URLSearchParams({ platform, limit: limit.toString() });
    if (type) params.set('type', type);
    return fetchApi<ChatContact[]>(`/contacts?${params}`);
  },

  getConversations: (platform: Platform, limit = 100) =>
    fetchApi<ChatConversation[]>(`/conversations?platform=${platform}&limit=${limit}`),

  getMessages: (conversationId: string, platform: Platform, limit = 200, before?: number) => {
    const params = new URLSearchParams({ platform, limit: limit.toString() });
    if (before) params.set('before', before.toString());
    return fetchApi<ChatMessage[]>(`/messages/conversation/${conversationId}?${params}`);
  },

  search: (query: string, platform: Platform, limit = 50) =>
    fetchApi<SearchResult[]>(`/search?q=${encodeURIComponent(query)}&platform=${platform}&limit=${limit}`),

  getStats: (platform: Platform) =>
    fetchApi<StatsOverview>(`/stats/overview?platform=${platform}`),

  startImport: (platform: Platform, range: string = 'all') =>
    fetchApi<{ task_id: string; status: string; platform: string }>(`/import/${platform}?range=${range}`, { method: 'POST' }),

  getImportStatus: (taskId: string) =>
    fetchApi<any>(`/import/status/${taskId}`),
};
