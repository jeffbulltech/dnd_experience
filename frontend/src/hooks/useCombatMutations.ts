import { useMutation, useQueryClient } from "@tanstack/react-query";

import { api } from "../services/api";
import { CombatState } from "../types";

type ParticipantPayload = {
  name: string;
  initiative: number;
  hit_points: number;
  max_hit_points: number;
  armor_class: number;
  conditions?: string[];
  attributes?: Record<string, unknown>;
};

type ParticipantUpdatePayload = Partial<ParticipantPayload>;

export function useCombatMutations(campaignId?: number) {
  const queryClient = useQueryClient();

  const invalidate = () => {
    queryClient.invalidateQueries({ queryKey: ["combat-state", campaignId] });
  };

  const addParticipant = useMutation({
    mutationFn: async (payload: ParticipantPayload) => {
      if (!campaignId) throw new Error("campaignId is required");
      const response = await api.post<CombatState>(`/combat/${campaignId}/participants`, payload);
      return response.data;
    },
    onSuccess: invalidate
  });

  const updateParticipant = useMutation({
    mutationFn: async ({ participantId, updates }: { participantId: number; updates: ParticipantUpdatePayload }) => {
      if (!campaignId) throw new Error("campaignId is required");
      const response = await api.put<CombatState>(
        `/combat/${campaignId}/participants/${participantId}`,
        updates
      );
      return response.data;
    },
    onSuccess: invalidate
  });

  const deleteParticipant = useMutation({
    mutationFn: async (participantId: number) => {
      if (!campaignId) throw new Error("campaignId is required");
      const response = await api.delete<CombatState>(`/combat/${campaignId}/participants/${participantId}`);
      return response.data;
    },
    onSuccess: invalidate
  });

  return {
    addParticipant,
    updateParticipant,
    deleteParticipant
  };
}

