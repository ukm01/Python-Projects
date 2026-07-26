import { useCallback, useState } from "react";

import { askQuestion } from "@/api/chat-api";
import type { ChatResponse } from "@/api/types";
import { useApiAction } from "@/hooks/api/use-api-action";


export type ChatMessage =
  | {
      id: string;
      role: "user";
      content: string;
    }
  | {
      id: string;
      role: "assistant";
      content: string;
      response: ChatResponse;
    };

export function useChat() {
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const chatAction = useApiAction(askQuestion);

  const sendQuestion = useCallback(
    async (rawQuestion: string) => {
      const question = rawQuestion.trim();
      if (!question || chatAction.isLoading) {
        return false;
      }

      const requestId = crypto.randomUUID();
      setMessages((current) => [
        ...current,
        {
          id: `${requestId}-user`,
          role: "user",
          content: question,
        },
      ]);

      const response = await chatAction.execute(question);
      if (!response) {
        return false;
      }

      setMessages((current) => [
        ...current,
        {
          id: `${requestId}-assistant`,
          role: "assistant",
          content: response.answer,
          response,
        },
      ]);
      return true;
    },
    [chatAction],
  );

  const clearConversation = useCallback(() => {
    setMessages([]);
    chatAction.clearError();
  }, [chatAction]);

  return {
    messages,
    sendQuestion,
    clearConversation,
    isLoading: chatAction.isLoading,
    error: chatAction.error,
    clearError: chatAction.clearError,
  };
}
