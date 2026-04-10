export type Platform = 'wechat' | 'qq' | 'feishu';

export interface SourceStatus {
  platform: Platform;
  source_dir: string;
  backup_dir: string;
  source_exists: boolean;
  backup_exists: boolean;
  last_backup: string | null;
  backup_file_count: number;
  backup_total_size: number;
  source_deleted: boolean;
}

export interface BackupResult {
  platform: Platform;
  status: string;
  total_files: number;
  new_files: number;
  updated_files: number;
  skipped_files: number;
  total_size: number;
  duration_ms: number;
  message: string;
}

export interface DeleteSourceResult {
  platform: Platform;
  status: string;
  deleted_files: number;
  failed_files: number;
  freed_size: number;
  errors: string[];
}

export interface BackupHistoryEntry {
  timestamp: string;
  platform: Platform;
  status: string;
  new_files: number;
  updated_files: number;
  skipped_files: number;
  total_size: number;
}

export interface ChatContact {
  id: string;
  platform: Platform;
  name: string | null;
  alias: string | null;
  remark: string | null;
  type: 'user' | 'group';
  avatar_url: string | null;
}

export interface ChatConversation {
  id: string;
  platform: Platform;
  contact_id: string | null;
  title: string | null;
  last_message_time: number | null;
  message_count: number;
  contact_name: string | null;
  last_message_preview: string | null;
}

export interface ChatMessage {
  id: string;
  platform: Platform;
  conversation_id: string;
  sender_id: string | null;
  sender_name: string | null;
  content: string | null;
  msg_type: string;
  timestamp: number;
  extra_json: string | null;
  sender_avatar?: string | null;
}

export interface SearchResult {
  message_id: string;
  conversation_id: string;
  platform: Platform;
  sender_name: string | null;
  snippet: string;
  timestamp: number;
  highlights: string[];
}

export interface StatsOverview {
  total_contacts: number;
  total_conversations: number;
  total_messages: number;
  platform_stats: Record<Platform, { messages: number; conversations: number; contacts: number }>;
}

export const PLATFORM_LABELS: Record<Platform, string> = {
  wechat: '微信',
  qq: 'QQ',
  feishu: '飞书',
};

export const PLATFORM_ICONS: Record<Platform, string> = {
  wechat: '💚',
  qq: '🐧',
  feishu: '🐦',
};

export function formatBytes(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(1)) + ' ' + sizes[i];
}

export function formatTimeAgo(ts: number | null): string {
  if (!ts) return '';
  const diff = Date.now() - ts;
  if (diff < 60000) return '刚刚';
  if (diff < 3600000) return `${Math.floor(diff / 60000)}分钟前`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)}小时前`;
  if (diff < 604800000) return `${Math.floor(diff / 86400000)}天前`;
  const d = new Date(ts);
  return `${d.getMonth() + 1}/${d.getDate()}`;
}
