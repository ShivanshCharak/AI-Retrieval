"use client";

import { act, useEffect, useState } from "react";
import Sidebar from "@/components/sidebar/Sidebar";
import MainArea from "@/components/main/MainArea";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";


export default function ChatPage() {
    const [sidebarVisibility, setSidebarVisibility]= useState<boolean>(true)
  const [activeChat, setActiveChat] = useState<string | null>("1");
  const [conversationId, setConversationId] =
  useState<number | null>(null);
  const {login,  user} =useAuth()
  const router = useRouter()


  const handleNewChat = () => setActiveChat(null);
  useEffect(()=>{
    setConversationId(Number(activeChat))
  },[activeChat])

  useEffect(()=>{
     fetch("/api/auth/me",{
      credentials:"include"
    }).then(async (res)=>{
     try {
      if (res.ok){
      const data  = await res.json()
        login({name:data.username, email:data.email})

      }else if (res.status === 401){
        login(null)
        router.push("/login")
      }
     } catch (error) {
      console.error(error)
     }
    
    })

  },[])


  return (
    
      <div className="flex h-screen w-full font-sans">
        
        
        <Sidebar
          activeChat={activeChat}
          onSelect={setActiveChat}
          onNewChat={handleNewChat}
          sidebarVisibility={sidebarVisibility}
          setSidebarVisibility={setSidebarVisibility}
          
        />
        <MainArea
          userName={user?.name}
          sidebarVisibility={sidebarVisibility}
          conversationId={conversationId}
          setConversationId={setConversationId}
        />
      </div>
    
  );
}
