export interface Session {
  id: string;
  project_id: string;
  title: string;
  directory: string;
  time_created: number;
  time_updated: number;
  message_count?: number;
  project_name?: string;
}

export interface Message {
  id: string;
  session_id: string;
  time_created: number;
  data: string;
  parts?: Part[];
}

export interface Part {
  id: string;
  message_id: string;
  session_id: string;
  data: string;
}

export interface Project {
  id: string;
  name: string | null;
  directory: string;
  session_count?: number;
}

export interface SearchResult {
  session_id: string;
  session_title: string;
  message_id: string;
  snippet: string;
  highlights: string[];
}

export interface KnowledgeItem {
  id: string;
  session_id: string;
  category: string;
  content: string;
  created_at: string;
}

export interface StatsOverview {
  total_sessions: number;
  total_messages: number;
  total_projects: number;
}

export interface StatsTrend {
  date: string;
  sessions: number;
  messages: number;
}

export interface ProjectStats {
  project_name: string;
  session_count: number;
  message_count: number;
}

export interface TabContentMessage {
  role: string;
  content: string;
}

export interface TabContent {
  id: string;
  title: string;
  url?: string;
  markdown: string;
  messages: TabContentMessage[];
  source: string;
  created_at: number;
  updated_at: number;
  message_count?: number;
  char_count?: number;
  created_at_str?: string;
  updated_at_str?: string;
}

export type DataSource = 'kilo' | 'opencode';
