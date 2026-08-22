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
  console.log("grouos", groups)

  const firstTitle = groups?.[0]?.title ?? "";
  console.log("first",firstTitle)

  useEffect(() => {
    if (!firstTitle) {
      setTypedTitle("");
      return;
    }

    let index = 0;
    setTypedTitle("");

    const interval = setInterval(() => {
      if (index < firstTitle.length) {
        setTypedTitle(firstTitle.slice(0, index + 1));
        console.log("t",typedTitle)
        index++;
      } else {
        clearInterval(interval);
      }
    }, 50);

    return () => clearInterval(interval);
  }, [firstTitle]);

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
              {index === 0 ? typedTitle : group.title ?? "New Chat"}
            </button>
          </li>
        ))}
      </ul>
    </nav>
  );
}