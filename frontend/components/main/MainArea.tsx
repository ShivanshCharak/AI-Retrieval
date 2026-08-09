import { QUICK_ACTIONS } from "../../data/constants";
import OrbIcon from "../../app/chat/OrbIcon";
import Greeting from "../../app/chat/Greeting";
import ChatInputBox from "../../app/chat/ChatInputBox";
import QuickActions from "../../app/chat/QuickActions";
import ReactMarkdown from "react-markdown";
import { Paperclip } from "lucide-react";
import remarkGfm from "remark-gfm";
import { Copy, ThumbsDown, ThumbsUp, CloudLightning } from "lucide-react";

import { useState } from "react";
import { LoaderIcon } from "lucide-react";
import { Check } from "lucide-react";
import ResponseTime from "../tracenode";

interface MainAreaProps {
  userName?: string;
  sidebarVisibility: boolean;
}
type TraceNode = {
  node: string;
  latency_ms: number;
};

export default function MainArea({
  userName = "Toby",
  sidebarVisibility,
}: MainAreaProps) {
  const [status, setStatus] = useState<
    { stage: string; title: string; description: string }[]
  >([]);
  const [showCheck, setShowCheck] = useState<number | null>();
  const [traceNode, setTraceNode] = useState<TraceNode[]>();
  const [message, setMessage] = useState<
    {
      role: "user" | "assistant";
      content: string;
      loading: boolean;
      file?: { name: string; type: string };
    }[]
  >([]);
  const [isChatting, setIsChatting] = useState<boolean>(false);
  const handleSend = (content: string, model: string, file?: File) => {
    setMessage((prev) => [
      ...prev,
      {
        role: "user",
        content,
        loading: false,
        file: file
          ? {
              name: file.name,
              type: file.type,
            }
          : undefined,
      },
      {
        role: "assistant",
        content: "",
        loading: true,
      },
    ]);
  };
  return (
    <main
      className={`flex-1 flex flex-col items-center justify-center gap-8 bg-gray-50 px-6 ${sidebarVisibility ? "w-[83%]" : "w-[97%]"} overflow-y-scroll`}
    >
      <div className="flex flex-col items-center gap-5">
        {message.length == 0 ? (
          <>
            <OrbIcon />
            <Greeting name={userName} />
          </>
        ) : (
          <></>
        )}
      </div>
      <div className="w-full top-20 absolute max-w-2xl flex flex-col gap-2 overflow-y-auto ">
        {message.map((msg, i) => (
          <div
            key={i}
            className={`w-full flex flex-col ${
              msg.role === "user" ? "items-end" : "items-start"
            }`}
          >
            {/* Message bubble */}
            <div
              className={`px-3 py-2 rounded-lg text-sm w-fit max-w-[80%] ${
                msg.role === "user"
                  ? "bg-black text-white"
                  : "bg-gray-200 text-black"
              }`}
            >
              {msg.loading ? (
                <LoaderIcon className="animate-spin" size={16} />
              ) : (
                <>
                  {msg.role === "user" && msg.file && (
                    <div className="mb-2 flex items-center gap-2 rounded-lg border border-gray-500 bg-gray-800 px-3 py-2 w-fit">
                      <Paperclip size={14} />
                      <span>{msg.file.name}</span>
                    </div>
                  )}

                  <ReactMarkdown remarkPlugins={[remarkGfm]}>
                    {msg.content}
                  </ReactMarkdown>
                </>
              )}
            </div>
            {msg.role === "assistant" && !msg.loading && (
              <div className="flex items-center gap-2 mt-2 items-start">
                {[Copy, ThumbsDown, ThumbsUp, CloudLightning].map(
                  (Icon, index) => (
                    <button
                      key={index}
                      onClick={() => {
                        setShowCheck(index);

                        setTimeout(() => {
                          setShowCheck(null);
                        }, 1500);
                      }}
                      className="bg-transparent hover:bg-gray-200 p-1 rounded-sm cursor-pointer"
                    >
                      {showCheck === index ? (
                        <Check size={16} />
                      ) : (
                        <Icon size={16} />
                      )}
                    </button>
                  ),
                )}

                {traceNode && <ResponseTime trace={traceNode} />}
              </div>
            )}
          </div>
        ))}
      </div>

      <ChatInputBox
        onSend={handleSend}
        setMessage={setMessage}
        chatting={isChatting}
        setChatting={setIsChatting}
        setTraceNode={setTraceNode}
        status={status}
        setStatus={setStatus}
      />

      {message.length > 0 ? "" : <QuickActions actions={QUICK_ACTIONS} />}
    </main>
  );
}
