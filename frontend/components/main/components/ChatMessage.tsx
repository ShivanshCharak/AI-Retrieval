import ReactMarkdown from "react-markdown";
import remarkGfm from "remark-gfm";
import { LoaderIcon, Paperclip } from "lucide-react";
import AssistantActions from "./AssistantAction";

export type ChatMessageData = {
  role: "user" | "assistant";
  content: string;
  loading: boolean;
  file?: {
    name: string;
    type: string;
  };
};

interface ChatMessageProps {
  message: ChatMessageData;
  traceNode: {
    node: string;
    latency_ms: number;
  }[];
}

export default function ChatMessage({
  message,
  traceNode,
}: ChatMessageProps) {
  const isUser = message.role === "user";

  return (
    <div
      className={`w-full flex flex-col ${
        isUser ? "items-end" : "items-start"
      }`}
    >
      <div
        className={`px-3 py-2 rounded-lg text-sm w-fit max-w-[80%] ${
          isUser
            ? "bg-black text-white"
            : "bg-gray-200 text-black"
        }`}
      >
        {message.loading ? (
          <LoaderIcon
            className="animate-spin"
            size={16}
          />
        ) : (
          <>
            {isUser && message.file && (
              <div className="mb-2 flex items-center gap-2 rounded-lg border border-gray-500 bg-gray-800 px-3 py-2 w-fit">
                <Paperclip size={14} />

                <span>{message.file.name}</span>
              </div>
            )}

            <ReactMarkdown remarkPlugins={[remarkGfm]}>
              {message.content}
            </ReactMarkdown>
          </>
        )}
      </div>

      {!isUser && !message.loading && (
        <AssistantActions traceNode={traceNode} />
      )}
    </div>
  );
}