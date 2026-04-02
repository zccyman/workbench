interface MessageBubbleProps {
  data: { role: string; content: string };
  createdAt?: string | number;
}

export function MessageBubble({ data }: MessageBubbleProps) {
  const isUser = data.role === 'user';

  return (
    <div className={`flex gap-3 ${isUser ? 'flex-row-reverse' : ''}`}>
      <div className={`w-8 h-8 rounded-lg flex items-center justify-center flex-shrink-0 text-xs font-bold text-white ${
        isUser ? 'bg-blue-500' : 'bg-purple-500'
      }`}>
        {isUser ? 'U' : 'AI'}
      </div>
      <div className={`max-w-[80%] rounded-lg p-3 text-sm leading-relaxed ${
        isUser
          ? 'bg-blue-500 text-white'
          : 'bg-gray-100 dark:bg-gray-800 text-gray-900 dark:text-gray-100'
      }`}>
        {data.content?.split('```').map((block, i) => {
          if (i % 2 === 1) {
            const lines = block.split('\n');
            const lang = lines[0];
            const code = lines.slice(1).join('\n');
            return (
              <pre key={i} className="mt-2 mb-2 p-3 rounded-md overflow-x-auto text-xs" style={{background: isUser ? 'rgba(0,0,0,0.15)' : '#FFFFFF'}}>
                {lang && <span className="text-xs opacity-60 block mb-1">{lang}</span>}
                <code>{code}</code>
              </pre>
            );
          }
          return <span key={i}>{block}</span>;
        })}
      </div>
    </div>
  );
}
