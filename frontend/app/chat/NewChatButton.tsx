import { Plus } from "lucide-react";

interface NewChatButtonProps {
  onClick?: () => void;
  visibility: boolean
}

export default function NewChatButton({ onClick, visibility }: NewChatButtonProps) {
  return (
    <div className="flex w-full justify-center">
      <button
        onClick={onClick}
        className={` hover:cursor-pointer ${"w-[90%] rounded-full flex justify-center"} flex items-center absolute  justify-center gap-2  bg-gray-900 hover:bg-gray-800   text-white text-sm font-medium rounded-xl py-2.5 transition-colors`}
      >
        <Plus size={16} />
        {visibility && <span>New chat</span>}
      </button>
    </div>
  );
}
