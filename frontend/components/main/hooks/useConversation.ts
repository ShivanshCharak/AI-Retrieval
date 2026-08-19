import { useCallback } from "react";
import { ChatMessageData } from "../components/ChatMessage";

interface UseConversationProps {
  conversationId: number | null;
  setConversationId: React.Dispatch<
    React.SetStateAction<number | null>
  >;
  setMessages: React.Dispatch<
    React.SetStateAction<ChatMessageData[]>
  >;
}


export function useConversation({
  conversationId,
  setConversationId,
  setMessages,
}: UseConversationProps) {
  const sendMessage = useCallback(
    async (
      content: string,
      model: string,
      file?: File
    ) => {
      setMessages((prev) => [
        ...prev,
        {
          role: "user",
          content,
          loading: false,
          file: file
            ? {
                name: file.name,
                type: file.type,
              }
            : undefined,
        },
        {
          role: "assistant",
          content: "",
          loading: true,
        },
      ]);

      if (!conversationId) {
        const formData = new FormData();

        formData.append("message", content);

        if (file) {
          formData.append(
            "uploaded_files",
            file
          );
        }

        const response = await fetch(
          "http://localhost:8000/api/v1/conversation",
          {
            method: "POST",
            body: formData,
            credentials: "include",
          }
        );

        const data = await response.json();

        setConversationId(
          data.conversation_id
        );

        return;
      }

      await fetch(
        `http://localhost:8000/api/v1/conversation/${conversationId}/message`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
          },
          credentials: "include",
          body: JSON.stringify({
            role: "user",
            content,
          }),
        }
      );
    },
    [
      conversationId,
      setConversationId,
      setMessages,
    ]
  );

  return {
    sendMessage,
  };
}