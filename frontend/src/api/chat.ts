import { apiFetch } from "./client";
import type { Gap, GraphExport } from "../types";

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export async function sendChatMessage(
  messages: ChatMessage[],
  graphData: GraphExport | null,
  gaps: Gap[]
): Promise<string> {
  const res = await apiFetch<{ reply: string }>("/chat", {
    method: "POST",
    body: JSON.stringify({ messages, graph_data: graphData, gaps }),
  });
  return res.reply;
}
