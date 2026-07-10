import { LucideIcon } from "lucide-react";

export interface ChatItem {
  id: string;
  title: string;
}

export interface ChatGroup {
  label: string;
  items: ChatItem[];
}

export interface NavLink {
  label: string;
  icon: LucideIcon;
}

export interface QuickAction {
  label: string;
  icon: LucideIcon;
}
