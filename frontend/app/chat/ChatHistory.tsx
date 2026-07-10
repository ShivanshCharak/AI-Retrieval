import { ChatGroup } from "./types";

interface ChatHistoryProps {
  groups: ChatGroup[];
  activeId: string | null;
  onSelect: (id: string) => void;
}

export default function ChatHistory({ groups, activeId, onSelect }: ChatHistoryProps) {
  return (
    <nav className="flex-1 mt-[50px] overflow-y-auto px-3 space-y-5">
      {groups.map((group) => (
        <div key={group.label}>
          <p className="text-xs font-semibold text-gray-400 mb-1 px-1">{group.label}</p>
          <ul className="space-y-0.5">
            {group.items.map((item) => (
              <li key={item.id}>
                <button
                  onClick={() => onSelect(item.id)}
                  className={`w-full text-left text-sm px-2 py-1.5 rounded-md transition-colors truncate  cursor-pointer ${
                    activeId === item.id
                      ? "bg-gray-100 text-gray-900 font-medium"
                      : "text-gray-600 hover:bg-gray-50 hover:text-gray-800"
                  }`}
                >
                  {item.title}
                </button>
              </li>
            ))}
          </ul>
        </div>
      ))}
    </nav>
  );
}
