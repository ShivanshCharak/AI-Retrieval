import { Plus } from "lucide-react";
import { useEffect } from "react";
import ChatHistory from "./ChatHistory";

interface NewChatButtonProps {
  title: string;
  visibility: boolean;
  setChatHistory: React.Dispatch<React.SetStateAction<any[]>>;
  onSelect: (conversationId: number) => void;
}

export default function NewChatButton({
  visibility,
  chatHistory,
  setChatHistory,
  onSelect,
  title,
}: NewChatButtonProps) {

  // Update the newly created chat when AI generates the title
  useEffect(() => {
    if (!title) return;

    setChatHistory((prev) =>
      prev.map((chat, index) =>
        index === 0
          ? {
              ...chat,
              title: title,
            }
          : chat
      )
    );
  }, [title, setChatHistory]);

  const handleNewChat = async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/v1/conversation/new",
        {
          method: "POST",
          credentials: "include",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to create conversation");
      }

      const data = await response.json();

      console.log("Created:", data, chatHistory);
    

      localStorage.clear();

      setChatHistory((prev) => [
        {
          id: data.conversation_id,
          title: title ?? "",
        },
        ...prev,
      ]);

      onSelect(data.conversation_id);

    } catch (error) {
      console.error("Failed to create new chat:", error);
    }
  };

  return (
    <div className="flex w-full justify-center">
      <button
        onClick={handleNewChat}
        className="hover:cursor-pointer w-[90%] rounded-full flex items-center justify-center gap-2 bg-gray-900 hover:bg-gray-800 text-white text-sm font-medium rounded-xl py-2.5 transition-colors"
      >
        <Plus size={16} />

        {visibility && <span>New chat</span>}
      </button>
    </div>
  );
}