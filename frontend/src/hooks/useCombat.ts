import { useQuery } from "@tanstack/react-query";

import { api } from "../services/api";
import { CombatState } from "../types";

async function fetchCombatState(campaignId: number): Promise<CombatState> {
  const response = await api.get<CombatState>(`/combat/state/${campaignId}`);
  return response.data;
}

export function useCombatState(campaignId?: number) {
  return useQuery({
    queryKey: ["combat-state", campaignId],
    queryFn: () => {
      if (!campaignId) {
        throw new Error("campaignId is required");
      }
      return fetchCombatState(campaignId);
    },
    enabled: Boolean(campaignId),
    refetchInterval: 5000,
    staleTime: 1000 * 5,
  });
}

