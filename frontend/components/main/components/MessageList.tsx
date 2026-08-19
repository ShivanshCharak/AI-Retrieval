import ChatMessage, {
  ChatMessageData,
} from "./ChatMessage";

interface MessageListProps {
  messages: ChatMessageData[];
  traceNode: {
    node: string;
    latency_ms: number;
  }[];
}

export default function MessageList({
  messages,
  traceNode,
}: MessageListProps) {
  return (
    <div className="flex flex-col gap-2 w-[50%]">
      {messages.map((message, index) => (
        <ChatMessage
          key={index}
          message={message}
          traceNode={traceNode}
        />
      ))}
    </div>
  );
}