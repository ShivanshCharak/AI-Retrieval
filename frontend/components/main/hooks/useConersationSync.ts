import { useEffect, useRef } from "react";

type ChatMessage = {
  role: "user" | "assistant";
  content: string;
  loading: boolean;
  file?: {
    name: string;
    type: string;
  };
};

export function useConversationSync(
  conversationId: number | null,
  messages: ChatMessage[]
) {
  const messagesRef = useRef(messages);

  useEffect(() => {
    messagesRef.current = messages;
  }, [messages]);

  useEffect(() => {
    if (!conversationId) {
      return;
    }

    const syncConversation = async () => {
      const messagesToSave =
        messagesRef.current.filter(
          (msg) => !msg.loading
        );

      if (messagesToSave.length === 0) {
        return;
      }

      try {
        await fetch(
          `http://localhost:8000/api/v1/conversation/${conversationId}/sync`,
          {
            method: "PUT",
            headers: {
              "Content-Type": "application/json",
            },
            credentials: "include",
            body: JSON.stringify({
              messages: messagesToSave.map((msg) => ({
                role: msg.role,
                content: msg.content,
              })),
            }),
          }
        );

        console.log("Conversation synced");
      } catch (error) {
        console.error(
          "Failed to sync conversation:",
          error
        );
      }
    };

    const interval = setInterval(
      syncConversation,
      10_000
    );

    return () => {
      clearInterval(interval);
    };
  }, [conversationId]);
}