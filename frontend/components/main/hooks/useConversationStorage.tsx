import { useEffect } from "react";

export function useConversationStorage<T>(
  storageKey: string,
  messages: T[],
  setMessages: React.Dispatch<React.SetStateAction<T[]>>
) {
  useEffect(() => {
    const saved = localStorage.getItem(storageKey);

    if (!saved) {
      console.log("message1 in useConversationStorage")
      setMessages([]);
      return;
    }

    try {
      console.log("message2 in useConversationStorage")
      setMessages(JSON.parse(saved));
    } catch (error) {
      console.error(
        "Failed to load conversation:",
        error
      );
      console.log("message3 in useConversationStorage")
      setMessages([]);
    }
  }, [storageKey, setMessages]);

  useEffect(() => {
    if (messages.length === 0) {
      console.log("message lentgh is 0")
      return;
    }

    localStorage.setItem(
      storageKey,
      JSON.stringify(messages)
    );
  }, [messages, storageKey]);
}