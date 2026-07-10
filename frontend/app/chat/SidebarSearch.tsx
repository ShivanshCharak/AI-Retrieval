import { Search } from "lucide-react";

export default function SidebarSearch() {
  return (
    <div className="px-1 ">
      <div className="flex items-center gap-2 bg-gray-50 border border-gray-200 rounded-lg px-3 py-2">
        <Search size={14} className="text-gray-400 shrink-0" />
        <input
          type="text"
          placeholder="Search chats..."
          className="bg-transparent text-sm text-gray-600 placeholder-gray-400 outline-none w-full"
        />
        <span className="text-xs text-gray-400 font-medium ml-auto shrink-0">⌘K</span>
      </div>
    </div>
  );
}
