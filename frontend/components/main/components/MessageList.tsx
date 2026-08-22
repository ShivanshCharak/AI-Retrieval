import ChatMessage, {
  ChatMessageData,
} from "./ChatMessage";
// import Sources, { Source } from "";
import Sources, {Source} from "@/components/sources";

interface MessageListProps {
  messages: ChatMessageData[];
  traceNode: {
    node: string;
    latency_ms: number;
  }[];
  sources?: Source[];
}

export default function MessageList({
  messages,
  traceNode,
  sources = [],
}: MessageListProps) {
  return (
    <div className="flex flex-col gap-2 w-[50%]">
     
      {messages.map((message, index) => (
        <div key={index}>
          <ChatMessage
            message={message}
            traceNode={traceNode}
          />

          {/* Show sources after the assistant message */}
          {message.role === "assistant" && index === messages.length - 1 && (
            <Sources sources={sources} />
          )}
        </div>
      ))}
    </div>
  );
}