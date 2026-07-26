import { apiRequest, jsonRequestBody } from "@/api/client";
import type { ChatResponse } from "@/api/types";


export function askQuestion(question: string) {
  return apiRequest<ChatResponse>("/chat/ask", {
    method: "POST",
    authenticated: true,
    ...jsonRequestBody({ question }),
  });
}
