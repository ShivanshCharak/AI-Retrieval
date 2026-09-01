"use client";

import { NAV_LINKS } from "@/data/constants";
import SidebarSearch from "../../app/chat/SidebarSearch";
import ChatHistory from "../../app/chat/ChatHistory";
import SidebarNav from "../../app/chat/SidebarNav";
import NewChatButton from "../../app/chat/NewChatButton";
import { Menu } from "lucide-react";
import AuthBlock from "../UserInfo";
import { SetStateAction, useEffect } from "react";
import useChatHistory from "./hooks/useChatHistory";

interface SidebarProps {
  activeChat: string | null;
  onSelect: (id: string) => void;
  title: string;
  sidebarVisibility: boolean;
  setSidebarVisibility: React.Dispatch<SetStateAction<boolean>>;
}

export default function Sidebar({
  activeChat,
  onSelect,
  sidebarVisibility,
  title,
  setSidebarVisibility,
}: SidebarProps) {
 
  const {
    chatHistory,
    setChatHistory,
    refreshChatHistory,
  } = useChatHistory();

  useEffect(() => {
    refreshChatHistory();
  }, [refreshChatHistory]);

  // Handle sidebar responsive behavior
  useEffect(() => {
    const handleResize = () => {
      if (window.innerWidth <= 1500) {
        setSidebarVisibility(false);
      }
    };

    handleResize();

    window.addEventListener("resize", handleResize);

    return () => {
      window.removeEventListener("resize", handleResize);
    };
  }, [setSidebarVisibility]);

  console.log("chat history:", chatHistory);
  console.log("title:", title);

  return (
    <aside
      className={`
        relative
        flex
        flex-col
        h-screen
        shrink-0
        bg-white
        border-r
        border-gray-100
        transition-all
        duration-300
        ease-in-out
        ${sidebarVisibility ? "w-[280px]" : "w-[56px]"}
      `}
    >
      {/* Header */}
      <div className="shrink-0 flex items-center px-3 pt-5 pb-3">
        {sidebarVisibility && <SidebarSearch />}

        <Menu
          color="gray"
          className="cursor-pointer mt-1 ml-1 shrink-0"
          onClick={() =>
            setSidebarVisibility((prev) => !prev)
          }
        />
      </div>

      {/* New chat */}
      <div className="shrink-0 px-3">
        <NewChatButton
          title={title}
          chatHistiry ={chatHistory}
          setChatHistory={setChatHistory}
          visibility={sidebarVisibility}
          onSelect={onSelect}
        />
      </div>

      {/* Chat history */}
      {sidebarVisibility && (
        <div className="min-h-0 flex-1">
          <div className="px-3 mt-5 mb-2">
            <span className="text-xs font-semibold text-gray-500">
              Recents
            </span>
          </div>

          <ChatHistory
            groups={chatHistory}
            activeId={activeChat}
            onSelect={onSelect}
          />
        </div>
      )}

      {/* Bottom */}
      <div className="shrink-0 bg-white border-t border-gray-100 px-3 py-3">
        <SidebarNav
          links={NAV_LINKS}
          visibility={sidebarVisibility}
        />

        <div className="mt-2">
          <AuthBlock sidebarVisibility={sidebarVisibility} />
        </div>
      </div>
    </aside>
  );
}