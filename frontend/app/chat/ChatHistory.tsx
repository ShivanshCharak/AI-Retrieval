import { ChatGroup } from "./types";
import Link from "next/link";

interface ChatHistoryProps {
  groups: ChatGroup[];
  activeId: string | null;
  onSelect: (id: string) => void;
}

export default function ChatHistory({
  groups,
  activeId,
  onSelect,
}: ChatHistoryProps) {
  return (
    <nav className="flex-1 mt-[50px] overflow-y-auto px-3">
        <ul className="space-y-0.5">

          { groups && groups.length> 0 &&groups.map((group) => (
            <li key={group.id}>
              
              <button
                onClick={() => onSelect(String(group.id))}
                className={`w-full text-left text-sm px-2 py-1.5 rounded-md transition-colors truncate cursor-pointer ${
                  activeId === String(group.id)
                    ? "bg-gray-100 text-gray-900 font-medium"
                    : "text-gray-600 hover:bg-gray-50 hover:text-gray-800"
                }`}
              >
                {console.log(group.title)}
                {group.title}
              </button>
    
            </li>
          ))}
        </ul>
      </nav>
  );
}