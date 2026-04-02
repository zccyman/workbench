import { useState, useEffect, useCallback } from 'react';
import { aiSessionApi } from './api';
import type { Session, Project, SearchResult, StatsOverview, StatsTrend, ProjectStats, KnowledgeItem, DataSource, Message, TabContent } from './types';

export function useProjects(source: DataSource) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    aiSessionApi.getProjects(source)
      .then(setProjects)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [source]);

  return { projects, loading, error };
}

export function useSessions(source: DataSource, projectId?: string) {
  const [sessions, setSessions] = useState<Session[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    aiSessionApi.getSessions({ source, project_id: projectId || undefined, limit: 500 })
      .then(data => {
        setSessions(data);
      })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [source, projectId]);

  return { sessions, loading, error };
}

export function useSession(source: DataSource, sessionId: string | null) {
  const [session, setSession] = useState<Session | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) { setSession(null); return; }
    setLoading(true);
    aiSessionApi.getSession(sessionId, source)
      .then(setSession)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [source, sessionId]);

  return { session, loading, error };
}

export function useMessages(source: DataSource, sessionId: string | null) {
  const [messages, setMessages] = useState<Message[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!sessionId) { setMessages([]); return; }
    setLoading(true);
    aiSessionApi.getMessages(sessionId, source)
      .then(setMessages)
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [source, sessionId]);

  return { messages, loading, error };
}

export function useSearch(source: DataSource, query: string) {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (!query.trim()) { setResults([]); return; }
    const timer = setTimeout(() => {
      setLoading(true);
      aiSessionApi.search(query, source)
        .then(setResults)
        .catch(e => setError(e.message))
        .finally(() => setLoading(false));
    }, 300);
    return () => clearTimeout(timer);
  }, [source, query]);

  return { results, loading, error };
}

export function useStats(source: DataSource) {
  const [overview, setOverview] = useState<StatsOverview | null>(null);
  const [trends, setTrends] = useState<StatsTrend[]>([]);
  const [projectStats, setProjectStats] = useState<ProjectStats[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    Promise.all([
      aiSessionApi.getStatsOverview(source),
      aiSessionApi.getStatsTrends(30, source),
      aiSessionApi.getStatsProjects(source),
    ])
      .then(([o, t, p]) => { setOverview(o); setTrends(t); setProjectStats(p); })
      .catch(e => setError(e.message))
      .finally(() => setLoading(false));
  }, [source]);

  return { overview, trends, projectStats, loading, error };
}

export function useKnowledge(source: DataSource, sessionId: string | null) {
  const [items, setItems] = useState<KnowledgeItem[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const extract = useCallback(async () => {
    if (!sessionId) return;
    setLoading(true);
    setError(null);
    try {
      const data = await aiSessionApi.extractKnowledge(sessionId, source);
      setItems(data);
    } catch (e) {
      setError(e instanceof Error ? e.message : 'Failed');
    } finally {
      setLoading(false);
    }
  }, [source, sessionId]);

  return { items, loading, error, extract };
}

export function useTabContents(searchQuery: string) {
  const [contents, setContents] = useState<TabContent[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const loadContents = useCallback(async () => {
    setLoading(true);
    try {
      const data = searchQuery
        ? await aiSessionApi.searchTabContents(searchQuery)
        : await aiSessionApi.getTabContents();
      setContents(data);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, [searchQuery]);

  useEffect(() => {
    loadContents();
  }, [loadContents]);

  useEffect(() => {
    const interval = setInterval(() => {
      loadContents();
    }, 10000);
    return () => clearInterval(interval);
  }, [loadContents]);

  return { contents, loading, error, reload: loadContents, setContents };
}
