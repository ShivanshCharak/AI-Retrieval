"use client";

import { LayoutDashboard } from "lucide-react";
import { CHAT_HISTORY, NAV_LINKS } from "@/data/constants";
import SidebarSearch from "../../app/chat/SidebarSearch";
import ChatHistory from "../../app/chat/ChatHistory";
import SidebarNav from "../../app/chat/SidebarNav";
import NewChatButton from "../../app/chat/NewChatButton";
import { PanelRight, Menu } from "lucide-react";
import AuthBlock from "../UserInfo";
import {SetStateAction, useEffect, useState} from 'react' 

interface SidebarProps {
  activeChat: string | null;
  onSelect: (id: string) => void;
  onNewChat?: () => void;
  sidebarVisibility: boolean,
  setSidebarVisibility: React.Dispatch<SetStateAction<boolean>>
}



export default function Sidebar({ activeChat, onSelect, onNewChat, sidebarVisibility, setSidebarVisibility }: SidebarProps) {

  useEffect(() => {
  const handleResize = () => {
    if (window.innerWidth <= 1500) {
      setSidebarVisibility(false);
    }
  };

  handleResize(); 

  window.addEventListener("resize", handleResize);

  return () => {
    window.removeEventListener("resize", handleResize);
  };
}, [setSidebarVisibility]);
  return (
   <aside className={` relative ${sidebarVisibility ? "w-[17%]":"w-[50px] "} shrink-0 px-2  bg-white border-r border-gray-100 h-screen transition-all duration-300 ease-in-out `}>
      
      <div className=" flex alig px-1 pt-5 pb-3">
      {sidebarVisibility &&<SidebarSearch />}
      {/* <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="#000000" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="lucide lucide-panel-right-icon lucide-panel-right"><rect width="18" height="18" x="3" y="3" rx="2"/><path d="M15 3v18"/></svg> */}
     <Menu color="gray"  className="cursor-pointer mt-1 ml-1" onClick={()=>(
       setSidebarVisibility((prev)=> !prev)
      )} />
      </div>
      <NewChatButton onClick={onNewChat} visibility={sidebarVisibility} />


      {sidebarVisibility && <ChatHistory groups={CHAT_HISTORY} activeId={activeChat} onSelect={onSelect} />}
      <div className="absolute bottom-4 w-full">

        <SidebarNav links={NAV_LINKS} visibility={sidebarVisibility} />
        <AuthBlock  sidebarVisibility={sidebarVisibility}/>
      </div>
      {/* </div> */}
    
    </aside>
  );
}
