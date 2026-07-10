import { QuickAction } from "@/types";

interface QuickActionsProps {
  actions: QuickAction[];
  onAction?: (label: string) => void;
}

export default function QuickActions({ actions, onAction }: QuickActionsProps) {
  return (
    <div className="flex items-center gap-3 flex-wrap justify-center">
      {actions.map(({ label, icon: Icon }) => (
        <button
          key={label}
          onClick={() => onAction?.(label)}
          className="flex items-center gap-1.5 border border-gray-200 bg-white hover:bg-gray-50 text-gray-600 text-sm rounded-full px-4 py-1.5 transition-colors shadow-sm"
        >
          <Icon size={14} className="text-gray-400" />
          {label}
        </button>
      ))}
    </div>
  );
}
