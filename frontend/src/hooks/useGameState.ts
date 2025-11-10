import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../services/api";
import { GameState } from "../types";

async function fetchGameState(campaignId: number): Promise<GameState> {
  const response = await api.get<GameState>(`/game-state/${campaignId}`);
  return response.data;
}

export function useGameState(campaignId?: number) {
  return useQuery({
    queryKey: ["game-state", campaignId],
    queryFn: () => {
      if (!campaignId) {
        throw new Error("campaignId is required");
      }
      return fetchGameState(campaignId);
    },
    enabled: Boolean(campaignId),
    staleTime: 1000 * 15
  });
}

type GameStateUpdatePayload = Partial<Pick<GameState, "location" | "summary" | "active_quests" | "metadata">>;

export function useUpdateGameState(campaignId?: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (payload: GameStateUpdatePayload) => {
      if (!campaignId) {
        throw new Error("campaignId is required to update game state");
      }
      const response = await api.put<GameState>(`/game-state/${campaignId}`, payload);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["game-state", campaignId] });
    }
  });
}

