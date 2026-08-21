import { ChatGroup } from "./types";
import { useEffect, useState } from "react";


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
  const [typedTitle, setTypedTitle] = useState("");

  useEffect(() => {
    if (!groups?.length) return;

    const title = groups[0].title;
    setTypedTitle("");

    let index = 0;

    const interval = setInterval(() => {
      if (index < title.length) {
        setTypedTitle(title.slice(0, index + 1));
        index++;
      } else {
        clearInterval(interval);
      }
    }, 50);

    return () => clearInterval(interval);
  }, [groups]);

  return (
    <nav className="w-full h-full overflow-y-auto overflow-x-hidden px-2">
      <ul className="w-full space-y-1">
        {groups?.map((group, index) => (
          <li key={group.id} className="w-full">
            <button
              onClick={() => onSelect(String(group.id))}
              className={`
                w-full
                min-w-0
                text-left
                text-sm
                px-3
                py-2
                rounded-lg
                truncate
                border
                transition-colors
                cursor-pointer
                ${
                  activeId === String(group.id)
                    ? "bg-gray-100 border-gray-200 text-gray-900 font-medium"
                    : "border-transparent text-gray-600 hover:bg-gray-50 hover:border-gray-100 hover:text-gray-800"
                }
              `}
            >
              {index === 0 ? typedTitle : group.title}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}