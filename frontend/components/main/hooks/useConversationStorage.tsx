import { useEffect } from "react";

export function useConversationStorage<T>(
  storageKey: string,
  messages: T[],
  setMessages: React.Dispatch<React.SetStateAction<T[]>>
) {
  useEffect(() => {
    const saved = localStorage.getItem(storageKey);

    if (!saved) {
      setMessages([]);
      return;
    }

    try {
      setMessages(JSON.parse(saved));
    } catch (error) {
      console.error(
        "Failed to load conversation:",
        error
      );

      setMessages([]);
    }
  }, [storageKey, setMessages]);

  useEffect(() => {
    if (messages.length === 0) {
      return;
    }

    localStorage.setItem(
      storageKey,
      JSON.stringify(messages)
    );
  }, [messages, storageKey]);
}