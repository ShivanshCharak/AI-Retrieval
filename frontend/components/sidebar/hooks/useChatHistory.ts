import { useCallback, useState } from "react";

export default function useChatHistory() {
  const [chatHistory, setChatHistory] = useState<ChatGroup[]>([]);

  const refreshChatHistory = useCallback(async () => {
    try {
      const response = await fetch(
        "http://localhost:8000/api/v1/conversations",
        {
          credentials: "include",
          method: "GET",
        }
      );

      if (!response.ok) {
        throw new Error("Failed to fetch chat history");
      }

      const data = await response.json();
     

      setChatHistory(data.result);

      return data.result;
    } catch (error) {
      console.error("Failed to load chat history:", error);
      return [];
    }
  }, []);

  return {
    chatHistory,
    setChatHistory,
    refreshChatHistory,
  };
}