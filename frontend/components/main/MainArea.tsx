"use client";

import React, { useEffect, useState } from "react";

import { QUICK_ACTIONS } from "../../data/constants";

import OrbIcon from "../../app/chat/OrbIcon";
import Greeting from "../../app/chat/Greeting";
import ChatInputBox from "../../app/chat/ChatInputBox";
import QuickActions from "../../app/chat/QuickActions";

import MessageList from "./components/MessageList";

type TraceNode = {
  node: string;
  latency_ms: number;
};

interface MainAreaProps {
  userName?: string;
  sidebarVisibility: boolean;
  conversationId?: number | null;

  traceNode: TraceNode[];

  setTraceNode: React.Dispatch<React.SetStateAction<TraceNode[]>>;

  setConversationId: React.Dispatch<React.SetStateAction<number | null>>;
}

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  loading: boolean;

  file?: {
    name: string;
    type: string;
  };
};

export default function MainArea({
  userName,
  sidebarVisibility,
  conversationId,
  setConversationId,
  traceNode,
  setTraceNode,
}: MainAreaProps) {
  const [message, setMessage] = useState<ChatMessage[]>([]);
  const [isChatting, setIsChatting] = useState(false);

  const [status, setStatus] = useState<
    { stage: string; title: string; description: string }[]
  >([]);
  const [sources, setSources] = useState([]);

  useEffect(() => {
    if (conversationId == null) {
      setMessage([]);
      setSources([]);
      return;
    }

    const loadConversation = async () => {
      if(!conversationId) return
      console.log("converstaion getting loaded")
      try {
        const response = await fetch(
          `http://localhost:8000/api/v1/conversation/${conversationId}`,
          {
            credentials: "include",
          }
        );

        if (!response.ok) {
          throw new Error("Failed to fetch conversation");
        }

        const data = await response.json();
        console.log("converstaion getting loaded",data)

        setMessage(data.result?.messages ?? []);
        setSources(data.result?.sources ?? []);
      } catch (error) {
        console.error("Failed to load conversation:", error);
      }
    };

    loadConversation();
  }, [conversationId]);

  const hasMessages = message.length > 0;

  return (
    <main
      className={`
        flex-1
        flex
        flex-col
        bg-gray-50
        px-6
        overflow-hidden
        ${sidebarVisibility ? "w-[83%]" : "w-[97%]"}
      `}
    >
      {/* Single scroll region: either the centered greeting, or the
          message list. This is the ONLY place that switches based on
          hasMessages — the input box below never moves or repositions. */}
      <div className="flex-1 min-h-0 overflow-y-auto flex flex-col">
        {!hasMessages ? (
          <div className="flex-1 flex flex-col items-center justify-center">
            <OrbIcon />
            <Greeting name={userName ?? ""} />
            <QuickActions actions={QUICK_ACTIONS} />
          </div>
        ) : (
          <div className="w-full pt-[50px]">
            <div className="w-full flex justify-center">
              <MessageList
                messages={message}
                traceNode={traceNode}
                sources={sources}
              />
            </div>
            {/* Extra space so the last message isn't hidden behind the input */}
            <div className="h-[24px]" />
          </div>
        )}
      </div>

      {/* Input box: always rendered in this exact spot, no absolute/fixed
          positioning, no conditional wrapper classes. */}
      <div className="w-full flex justify-center py-4 shrink-0">
        <div className="w-full max-w-2xl">
          <ChatInputBox
            setMessage={setMessage}
            message={message}
            chatting={hasMessages}
            setChatting={setIsChatting}
            conversationId={conversationId ?? null}
            setConversationId={setConversationId}
            setTraceNode={setTraceNode}
            status={status}
            setStatus={setStatus}
          />
        </div>
      </div>
    </main>
  );
}