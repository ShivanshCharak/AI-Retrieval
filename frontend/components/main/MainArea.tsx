import { QUICK_ACTIONS } from "../../data/constants";
import OrbIcon from "../../app/chat/OrbIcon";
import Greeting from "../../app/chat/Greeting";
import ChatInputBox from "../../app/chat/ChatInputBox";
import QuickActions from "../../app/chat/QuickActions";


import { useConversationStorage } from "./hooks/useConversationStorage";
import { useConversation } from "./hooks/useConversation";
import { useConversationSync } from "./hooks/useConersationSync";

import MessageList from "./components/MessageList";

import { useState, useEffect } from "react";
type TraceNode = {
  node: string;
  latency_ms: number;
};

interface MainAreaProps {
  userName?: string;
  sidebarVisibility: boolean;
  conversationId?: number | null;
  traceNode: TraceNode[],
  setTraceNode: React.Dispatch<
    React.SetStateAction<TraceNode[]>
  >; 
  setConversationId: React.Dispatch<
    React.SetStateAction<number | null>
  >;
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
  setTraceNode
}: MainAreaProps) {
  const [message, setMessage] = useState<ChatMessage[]>([]);
  const [isChatting, setIsChatting] = useState(false);
  const [status, setStatus] = useState([]);
  const [sources, setSources] = useState([])


  useEffect(() => {
  if (!conversationId) {
    console.log("id",conversationId)
    setMessage([]);
    return;
  }

  console.log("tracenode in maiarea", traceNode)

  const loadConversation = async () => {
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

      console.log("Loaded conversation:", data);

      setMessage(data.result.messages ?? []);
      setSources(data.result.sources??[])
      

    } catch (error) {
      console.error("Failed to load conversation:", error);
    }
  };

  loadConversation();
}, [conversationId]);

  const storageKey = conversationId
    ? `conversation_${conversationId}`
    : "conversation_new";

  useConversationStorage(
    storageKey,
    message,
    setMessage
  );

  useConversationSync(
    conversationId,
    message
  );

  // Conversation API
  const { sendMessage } = useConversation({
    conversationId,
    setConversationId,
    setMessages: setMessage,
  });

  
  {console.log("message.length", message.length)}
return (
  <main
    className={`flex-1 flex flex-col bg-gray-50 px-6 ${
      sidebarVisibility ? "w-[83%]" : "w-[97%]"
    } relative overflow-hidden`}
  >
    {message.length === 0 ? (
      <div className="flex-1 w-full flex flex-col items-center justify-center">
        <OrbIcon />
        <Greeting name={userName ?? ""} />

        <div className="w-full max-w-2xl mt-6">
          <ChatInputBox
            onSend={sendMessage}
            setMessage={setMessage}
            message={message}
            chatting={false}
            setChatting={setIsChatting}
            conversationId={conversationId}
            setTraceNode={setTraceNode}
            status={status}
            setStatus={setStatus}
          />
        </div>

        <QuickActions actions={QUICK_ACTIONS} />
      </div>
    ) : (
      <div className="flex-1 flex flex-col min-h-0">
        <div className="flex-1 overflow-y-auto w-full pt-[50px] min-h-0">
          <div className="w-full flex justify-center">
            <MessageList
              messages={message}
              traceNode={traceNode}
              sources={sources}
            />
          </div>

          <div className="h-[400px]" />
        </div>
      </div>
    )}

    {/* ONE ChatInputBox */}
    {message.length > 0 && (
      <div className="w-full flex justify-center pb-4">
        <ChatInputBox
          onSend={sendMessage}
          setMessage={setMessage}
          message={message}
          chatting={true}
          setChatting={setIsChatting}
          conversationId={conversationId}
          setTraceNode={setTraceNode}
          status={status}
          setStatus={setStatus}
        />
      </div>
    )}
  </main>
);
}