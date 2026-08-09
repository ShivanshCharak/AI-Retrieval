import { NavLink } from "@/types";

interface SidebarNavProps {
  links: NavLink[];
  visibility: boolean
}

export default function SidebarNav({ links, visibility }: SidebarNavProps) {
  return (
    <div className="w-full px-4 border-t absolute bottom-[8rem]  border-gray-100 space-y-0.5">
      {links.map(({ label, icon: Icon }) => (
        <button
          key={label}
          className="flex items-center gap-2.5 w-full text-sm text-gray-600 hover:text-gray-900 hover:bg-gray-50 px-2 py-1.5 rounded-md transition-colors cursor-pointer"
        >
          <Icon size={15} className="text-gray-400" />
          {visibility ? label:""}
        </button>
      ))}
    </div>
  );
}
