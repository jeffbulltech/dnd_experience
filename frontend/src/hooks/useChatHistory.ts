import { useInfiniteQuery } from "@tanstack/react-query";

import { api } from "../services/api";
import { ChatHistoryPage } from "../types";

async function fetchChatHistoryPage(
  campaignId: number,
  limit: number,
  before?: number | null
): Promise<ChatHistoryPage> {
  const params: Record<string, unknown> = { campaign_id: campaignId, limit };
  if (before) {
    params.before = before;
  }
  const response = await api.get<ChatHistoryPage>("/chat/history", { params });
  return response.data;
}

export function useChatHistory(campaignId?: number, limit = 50) {
  return useInfiniteQuery({
    queryKey: ["chat-history", campaignId, limit],
    queryFn: ({ pageParam }) => {
      if (!campaignId) {
        throw new Error("campaignId is required to fetch chat history");
      }
      return fetchChatHistoryPage(campaignId, limit, pageParam);
    },
    initialPageParam: null as number | null,
    getNextPageParam: (lastPage) => (lastPage.has_more ? lastPage.next_cursor : undefined),
    enabled: Boolean(campaignId),
    staleTime: 1000 * 10,
  });
}
