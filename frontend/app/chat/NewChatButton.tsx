import { Plus } from "lucide-react";

interface NewChatButtonProps {

  visibility: boolean;
  setChatHistory
}
export default function NewChatButton({  visibility, setChatHistory }: NewChatButtonProps) {

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

    console.log("Created:", data);

    localStorage.clear();

    setChatHistory((prev) => [
      {
        id: data.conversation_id,
        title: data.title,
      },
      ...prev,
    ]);
  

  } catch (error) {
    console.error("Failed to create new chat:", error);
  }
};

  return (
    <div className="flex w-full justify-center">
      <button
        onClick={handleNewChat}
        className={` hover:cursor-pointer ${"w-[90%] rounded-full flex justify-center"} flex items-center absolute  justify-center gap-2  bg-gray-900 hover:bg-gray-800   text-white text-sm font-medium rounded-xl py-2.5 transition-colors`}
      >
        <Plus size={16} />
        {visibility && <span>New chat</span>}
      </button>
    </div>
  );
}
