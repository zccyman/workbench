import { MessageBubble } from './MessageBubble';

interface MessageThreadProps {
  messages: any[];
  loading: boolean;
}

function extractContent(msg: any): { role: string; content: string } {
  const pd = msg.parsed_data || {};
  if (pd.content) return { role: pd.role || 'assistant', content: pd.content };
  const parts = msg.parts || [];
  for (const part of parts) {
    try {
      const partData = typeof part.data === 'string' ? JSON.parse(part.data) : part.data;
      if (partData?.text) return { role: pd.role || 'assistant', content: partData.text };
    } catch {}
  }
  return { role: pd.role || 'assistant', content: '' };
}

export function MessageThread({ messages, loading }: MessageThreadProps) {
  if (loading) return <div className="flex justify-center py-12"><div className="w-6 h-6 border-2 border-blue-500 border-t-transparent rounded-full animate-spin" /></div>;
  if (!messages || messages.length === 0) return <div className="text-center py-12 text-gray-500 dark:text-gray-400">选择一个会话查看内容</div>;

  return (
    <div className="space-y-4 p-4">
      {messages.map((msg, i) => {
        const { role, content } = extractContent(msg);
        if (!content) return null;
        return <MessageBubble key={msg.id || i} data={{ role, content }} createdAt={msg.time_created} />;
      })}
    </div>
  );
}
