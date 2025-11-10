import { useQuery } from "@tanstack/react-query";

import { api } from "../services/api";
import { ChatHistoryEntry } from "../types";

async function fetchChatHistory(campaignId: number, limit = 50): Promise<ChatHistoryEntry[]> {
  const response = await api.get<ChatHistoryEntry[]>("/chat/history", {
    params: { campaign_id: campaignId, limit }
  });
  return response.data;
}

export function useChatHistory(campaignId?: number, limit = 50) {
  return useQuery({
    queryKey: ["chat-history", campaignId, limit],
    queryFn: () => {
      if (!campaignId) {
        throw new Error("campaignId is required to fetch chat history");
      }
      return fetchChatHistory(campaignId, limit);
    },
    enabled: Boolean(campaignId),
    staleTime: 1000 * 10
  });
}

