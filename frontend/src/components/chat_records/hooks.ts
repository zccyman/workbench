import { useState, useEffect, useCallback } from 'react';
import { chatRecordsApi } from './api';
import type { Platform, SourceStatus, ChatContact, ChatConversation, ChatMessage, SearchResult, StatsOverview } from './types';

export function useSources() {
  const [sources, setSources] = useState<SourceStatus[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const data = await chatRecordsApi.getSources();
      setSources(data);
      setError(null);
    } catch (e: any) {
      setError(e.message);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => { load(); }, [load]);
  return { sources, loading, error, reload: load };
}

export function useContacts(platform: Platform, type?: string) {
  const [contacts, setContacts] = useState<ChatContact[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    chatRecordsApi.getContacts(platform, type)
      .then(setContacts)
      .catch(() => setContacts([]))
      .finally(() => setLoading(false));
  }, [platform, type]);

  return { contacts, loading };
}

export function useConversations(platform: Platform) {
  const [conversations, setConversations] = useState<ChatConversation[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    chatRecordsApi.getConversations(platform)
      .then(setConversations)
      .catch(() => setConversations([]))
      .finally(() => setLoading(false));
  }, [platform]);

  return { conversations, loading };
}

export function useMessages(platform: Platform, conversationId: string | null) {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!conversationId) { setMessages([]); return; }
    setLoading(true);
    chatRecordsApi.getMessages(conversationId, platform)
      .then(setMessages)
      .catch(() => setMessages([]))
      .finally(() => setLoading(false));
  }, [platform, conversationId]);

  return { messages, loading };
}

export function useSearch(platform: Platform, query: string) {
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    if (!query.trim()) { setResults([]); return; }
    const timer = setTimeout(() => {
      setLoading(true);
      chatRecordsApi.search(query, platform)
        .then(setResults)
        .catch(() => setResults([]))
        .finally(() => setLoading(false));
    }, 300);
    return () => clearTimeout(timer);
  }, [platform, query]);

  return { results, loading };
}

export function useStats(platform: Platform) {
  const [stats, setStats] = useState<StatsOverview | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    chatRecordsApi.getStats(platform)
      .then(setStats)
      .catch(() => setStats(null))
      .finally(() => setLoading(false));
  }, [platform]);

  return { stats, loading };
}
