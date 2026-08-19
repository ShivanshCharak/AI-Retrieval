import {
  Compass,
  BookOpen,
  Clock,
  Zap,
  Globe,
  LayoutDashboard,
  Code2,
  Paintbrush,
} from "lucide-react";
import { ChatGroup, NavLink, QuickAction } from "@/types";

export const CHAT_HISTORY: ChatGroup[] = [
  {
    label: "Today",
    items: [
      { id: "1", title: "What's something you've lear..." },
      { id: "2", title: "Best travel experience" },
      { id: "3", title: "Favorite book" },
    ],
  },
  {
    label: "Yesterday",
    items: [{ id: "4", title: "If you could teleport anywher..." }],
  },
  {
    label: "7 Days Ago",
    items: [
      { id: "5", title: "What's one goal you want to ..." },
      { id: "6", title: "Favorite programming langu..." },
      { id: "7", title: "Learning new skills" },
      { id: "8", title: "Weekend plans" },
      { id: "9", title: "Evening reflections" },
    ],
  },
];

export default async function History(){

 try {
   const data  = await fetch("http://localhost:8000/api/v1/conversations",{
     credentials:'include',
     method:"get",
   })
   let parsedData = await data.json()
   console.log(parsedData)
 } catch (error) {
  console.error("SOmething went wrong")
 }
}
export const NAV_LINKS: NavLink[] = [
  { label: "Explore", icon: Compass },
  { label: "Library", icon: BookOpen },
  { label: "History", icon: Clock },
  { label: "Upgrade", icon: Zap },
];

export const QUICK_ACTIONS: QuickAction[] = [
  { label: "Summary", icon: LayoutDashboard },
  { label: "Code", icon: Code2 },
  { label: "Design", icon: Paintbrush },
  { label: "Research", icon: Globe },
];

export const MODELS: string[] = [
  "Claude 3.5 sonnet",
  "Claude 3 Opus",
  "Claude 3 Haiku",
];
