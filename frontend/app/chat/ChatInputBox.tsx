"use client";

import React, { useState, useRef, useEffect, SetStateAction } from "react";
import { Paperclip, Globe, Mic, ArrowUp, Glasses } from "lucide-react";
import { MODELS } from "@/data/constants";
import getChatHistory from "@/components/sidebar/hooks/useChatHistory";

type TraceNode = {
  node: string;
  latency_ms: number;
};

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  loading: boolean;
  file?: { name: string; type: string };
  sources?: unknown[];
  title?: string;
  confidence?: number;
  latency_ms?: number;
  blocked?: boolean;
  error?: boolean;
};

interface ChatInputBoxProps {
  chatting: boolean;
  setChatting: React.Dispatch<React.SetStateAction<boolean>>;
  setMessage: React.Dispatch<React.SetStateAction<ChatMessage[]>>;
  setStatus: React.Dispatch<
    SetStateAction<{ stage: string; title: string; description: string }[]>
  >;
  setTraceNode: React.Dispatch<SetStateAction<TraceNode[]>>;
  message: ChatMessage[];
  conversationId: number | null;
  setConversationId: React.Dispatch<React.SetStateAction<number | null>>;
}

export default function ChatInputBox({
  chatting = false,
  setMessage,
  setChatting,
  setTraceNode,
  conversationId,
  setConversationId,
  message,
  setStatus,
}: ChatInputBoxProps) {
  const [input, setInput] = useState("");
  const [selectedModel, setSelectedModel] = useState(MODELS[0]);
  const [file, setFile] = useState<File | null>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);
  const [webSearch, setWebSearch] = useState<boolean>(false);
  const [deepSearch, setDeepSearch] = useState<boolean>(false);
  const [sending, setSending] = useState(false);

  const{chatHistory, setChatHistory} = getChatHistory()

  useEffect(() => {
    if (message.length > 0) {
      setChatting(true);
    }
  }, [message, setChatting]);

  const updateLastAssistantMessage = (
    updater: (msg: ChatMessage) => ChatMessage
  ) => {
    setMessage((prev) => {
      const idx = [...prev]
        .reverse()
        .findIndex((m) => m.role === "assistant");

      if (idx === -1) return prev;

      const realIdx = prev.length - 1 - idx;
      const updated = [...prev];
      updated[realIdx] = updater(updated[realIdx]);
      return updated;
    });
  };

  const handleSend = async () => {
    const trimmed = input.trim();
    if (!trimmed || sending) return;

    const currentFile = file;
    const currentModel = selectedModel;

    // Clear input immediately so a slow response can't leave stale text.
    setInput("");
    setFile(null);
    setChatting(true);
    setSending(true);

    // Push the user message + a single assistant placeholder up front.
    setMessage((prev) => [
      ...prev,
      {
        role: "user",
        content: trimmed,
        loading: false,
        file: currentFile
          ? { name: currentFile.name, type: currentFile.type }
          : undefined,
      },
      {
        role: "assistant",
        content: "",
        loading: true,
      },
    ]);

    const formdata = new FormData();
    formdata.append("message", trimmed);
    formdata.append("model", currentModel);
    formdata.append("web_search", String(webSearch));
    formdata.append("deep_search", String(deepSearch));
    formdata.append(
      "conversation_id",
      conversationId != null ? String(conversationId) : ""
    );
    if (currentFile) {
      formdata.append("file", currentFile);
    }

    try {
      const res = await fetch("/api/chat", {
        credentials: "include",
        method: "POST",
        body: formdata,
      });

      if (!res.body) {
        updateLastAssistantMessage((m) => ({
          ...m,
          content: "⚠️ No response body from server.",
          loading: false,
          error: true,
        }));
        return;
      }

      const reader = res.body.getReader();
      const decoder = new TextDecoder();

      let buffer = "";
      let answer = "";

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });

        const events = buffer.split("\n\n");
        buffer = events.pop() ?? "";

        for (const event of events) {
          if (!event.startsWith("data: ")) continue;

          let data: any;
          try {
            data = JSON.parse(event.slice(6));
          } catch {
            continue;
          }

          switch (data.type) {
            case "progress": {
              setStatus((prev) => {
                const exists = prev.find((p) => p.stage === data.stage);
                if (exists) return prev;
                return [
                  ...prev,
                  {
                    stage: data.stage,
                    title: data.title,
                    description: data.description,
                  },
                ];
              });
              break;
            }

            case "token": {
              answer += data.content;
              updateLastAssistantMessage((m) => ({
                ...m,
                role: "assistant",
                content: answer,
                loading: false,
              }));
              break;
            }

            case "guardrail": {
              updateLastAssistantMessage((m) => ({
                ...m,
                role: "assistant",
                content: data.message || "Request blocked by guardrail.",
                loading: false,
                blocked: true,
              }));

              setStatus((prev) => [
                ...prev,
                {
                  stage: "guardrail",
                  title: "Request blocked",
                  description: data.message || "This request was blocked.",
                },
              ]);

              return; // stop consuming the stream
            }

            case "complete": {
              setTraceNode(data.trace || []);
             

              if (data.conversation_id != null && conversationId == null) {
                setConversationId(data.conversation_id);
              }
              console.log(data.title)
              setChatHistory(prev=>[
                data.title,
                ...prev
              ])
              updateLastAssistantMessage((m) => ({
                ...m,
                loading: false,
                sources: data.sources || [],
                title: data.title,
                confidence: data.confidence,
                latency_ms: data.latency_ms,
              }));
              break;
            }

            case "error": {
              updateLastAssistantMessage((m) => ({
                ...m,
                role: "assistant",
                content: data.message || "Something went wrong.",
                loading: false,
                error: true,
              }));
              break;
            }

            default:
              console.log("Unknown SSE event:", data);
              break;
          }
        }
      }
    } catch (err) {
      console.error("Chat stream error:", err);
      updateLastAssistantMessage((m) => ({
        ...m,
        content: "⚠️ Something went wrong while sending your message.",
        loading: false,
        error: true,
      }));
    } finally {
      setSending(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <div className="w-full bg-white rounded-2xl shadow-sm border border-gray-200 overflow-hidden">
      {/* Upgrade banner */}
      <div className="flex items-center gap-1 px-4 pt-3 pb-1">
        <span className="text-xs text-gray-500">
          Use our faster AI on Pro Plan
        </span>
        <span className="mx-1 text-gray-300">·</span>
        <button className="text-xs text-purple-500 font-semibold hover:underline">
          Upgrade
        </button>
      </div>

      <input
        ref={fileInputRef}
        type="file"
        accept=".pdf,.doc,.docx,.txt"
        className="hidden"
        onChange={(e) => {
          const f = e.target.files?.[0];
          if (!f) return;
          setFile(f);
        }}
      />

      {file && (
        <div className="mx-4 mt-2 mb-1 flex items-center justify-between bg-gray-200 w-[200px] rounded-lg px-3 py-2 text-xs text-gray-700">
          <div className="flex items-center gap-2">
            <svg
              xmlns="http://www.w3.org/2000/svg"
              width="24"
              height="24"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
              className="lucide lucide-book-open-icon lucide-book-open"
            >
              <path d="M12 7v14" />
              <path d="M3 18a1 1 0 0 1-1-1V4a1 1 0 0 1 1-1h5a4 4 0 0 1 4 4 4 4 0 0 1 4-4h5a1 1 0 0 1 1 1v13a1 1 0 0 1-1 1h-6a3 3 0 0 0-3 3 3 3 0 0 0-3-3z" />
            </svg>
            <span className="truncate max-w-[250px] w-[100px] font-semibold">
              {file.name}
            </span>
            <span>{file.type.split("/")[1]}</span>
          </div>

          <button
            onClick={() => setFile(null)}
            className="text-gray-500 hover:text-red-500"
          >
            ✕
          </button>
        </div>
      )}

      {/* Textarea */}
      <textarea
        value={input}
        onChange={(e) => setInput(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Ask me anything..."
        rows={2}
        className="w-full px-4 py-2 text-sm text-gray-700 placeholder-gray-400 outline-none resize-none bg-transparent"
      />

      {/* Toolbar */}
      <div className="flex items-center justify-between px-3 pb-3 gap-2 ">
        <div className="flex items-center gap-2">
          <button
            onClick={() => fileInputRef.current?.click()}
            className=" cursor-pointer p-1.5 rounded-lg hover:bg-gray-100 transition-colors text-gray-400 hover:text-gray-600"
          >
            <Paperclip size={16} />
          </button>

          <div className="flex items-center gap-1 border border-gray-200 rounded-full px-3 py-1 text-xs text-gray-600 hover:bg-gray-50 transition-colors">
            <Globe size={12} className="text-gray-400" />
            <select
              value={selectedModel}
              onChange={(e) => setSelectedModel(e.target.value)}
              className="bg-transparent outline-none cursor-pointer text-xs text-gray-600"
            >
              {MODELS.map((m) => (
                <option key={m}>{m}</option>
              ))}
            </select>
          </div>

          <button
            onClick={() => setWebSearch(!webSearch)}
            className={`px-7 cursor-pointer flex align-middle py-2 rounded-full transition-colors duration-200 ${
              webSearch ? "bg-black text-white" : "bg-gray-200 text-black"
            }`}
          >
            <Globe size={14} color={webSearch ? "white" : "gray"} />
            <label className=" cursor-pointer ml-2 font-semibold text-xs">
              Web Search
            </label>
          </button>

          <button
            onClick={() => setDeepSearch(!deepSearch)}
            className={`px-7 cursor-pointer flex align-middle py-2 rounded-full transition-colors duration-200 ${
              deepSearch ? "bg-black text-white" : "bg-gray-200 text-black"
            }`}
          >
            <Glasses size={14} color={deepSearch ? "white" : "gray"} />
            <label className=" cursor-pointer ml-2 font-semibold text-xs">
              Deep Search
            </label>
          </button>
        </div>

        <div className="flex items-center gap-2 ml-auto">
          <button className="p-1.5 rounded-lg hover:bg-gray-100 transition-colors text-gray-400 hover:text-gray-600">
            <Mic size={16} />
          </button>

          <button
            onClick={handleSend}
            disabled={!input.trim() || sending}
            className={`p-1.5 rounded-full transition-colors ${
              input.trim() && !sending
                ? "bg-gray-900 text-white hover:bg-gray-700"
                : "bg-gray-200 text-gray-400 cursor-not-allowed"
            }`}
          >
            <ArrowUp size={16} />
          </button>
        </div>
      </div>
    </div>
  );
}