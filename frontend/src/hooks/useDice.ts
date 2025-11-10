import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../services/api";
import { DiceRollLog, DiceRollResult } from "../types";

type DiceHistoryFilters = {
  campaignId?: number;
  characterId?: number;
  limit?: number;
};

async function fetchDiceHistory(filters: DiceHistoryFilters): Promise<DiceRollLog[]> {
  const response = await api.get<DiceRollLog[]>("/dice/history", {
    params: {
      campaign_id: filters.campaignId,
      character_id: filters.characterId,
      limit: filters.limit ?? 20
    }
  });
  return response.data;
}

type DiceRollPayload = {
  expression: string;
  campaign_id?: number;
  character_id?: number;
  roller_type?: "player" | "gm" | "system";
};

async function rollDice(payload: DiceRollPayload): Promise<DiceRollResult> {
  const response = await api.post<DiceRollResult>("/dice/roll", payload);
  return response.data;
}

export function useDiceHistory(filters: DiceHistoryFilters) {
  return useQuery({
    queryKey: ["dice-history", filters],
    queryFn: () => fetchDiceHistory(filters),
    enabled: Boolean(filters.campaignId || filters.characterId),
    staleTime: 1000 * 10
  });
}

export function useRollDice(filters: DiceHistoryFilters) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: rollDice,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["dice-history", filters] });
    }
  });
}

