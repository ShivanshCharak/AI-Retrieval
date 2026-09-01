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

      try {
 

        if (!conversationId) {
          const formData = new FormData();

          formData.append("message", content);
          formData.append("model", model);

          if (file) {
            formData.append("uploaded_files", file);
          }

          const response = await fetch(
            "http://localhost:8000/api/v1/conversation",
            {
              method: "POST",
              body: formData,
              credentials: "include",
            }
          );

         
          if (!response.ok) {
            let errorMessage = `Failed to create conversation (${response.status})`;

            try {
              const errorData = await response.json();

              errorMessage =
                errorData?.detail ||
                errorData?.message ||
                errorData?.error ||
                errorMessage;
            } catch {
              // Response wasn't JSON
            }

            throw new Error(errorMessage);
          }

          const data = await response.json();

          console.log("Create conversation response:", data);

          const newConversationId =
            data?.result?.conversation_id;

          if (!newConversationId) {
            throw new Error(
              "Conversation was created but no conversation ID was returned."
            );
          }

          setConversationId(newConversationId);

          return;
        }



        const response = await fetch(
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
              model,
            }),
          }
        );

        if (!response.ok) {
          let errorMessage = `Failed to send message (${response.status})`;

          try {
            const errorData = await response.json();

            errorMessage =
              errorData?.detail ||
              errorData?.message ||
              errorData?.error ||
              errorMessage;
          } catch {
            // Response wasn't JSON
          }

          throw new Error(errorMessage);
        }

        const data = await response.json();

        console.log("Send message response:", data);

        return data;
      } catch (error) {
        console.error("Conversation error:", error);

        const errorMessage =
          error instanceof Error
            ? error.message
            : "Something went wrong while sending your message.";

     

        setMessages((prev) => {
          const updated = [...prev];

          const lastMessageIndex =
            updated.length - 1;

          const lastMessage =
            updated[lastMessageIndex];

          if (
            lastMessage?.role === "assistant" &&
            lastMessage.loading
          ) {
            updated[lastMessageIndex] = {
              ...lastMessage,
              content: `⚠️ ${errorMessage}`,
              loading: false,
            };
          }

          return updated;
        });

        // Re-throw so the component can also react if needed
        throw error;
      }
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