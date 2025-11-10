import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../services/api";
import {
  CharacterDraft,
  CharacterDraftCreate,
  CharacterDraftStepUpdate
} from "../types";

type AbilityScoreStepPayload = {
  method: "standard_array" | "point_buy" | "manual";
  scores: Record<string, number>;
};

type OriginStepPayload = {
  species?: string;
  background?: string;
  languages?: string[];
};

type ClassStepPayload = {
  class: string;
};

type ProficiencyStepPayload = {
  skills: string[];
  tools?: string[];
  expertise?: string[];
};

type EquipmentStepPayload = {
  weapons?: string[];
  armor?: string[];
  packs?: string[];
  custom_items?: Array<{ name: string; description?: string }>;
  currency?: Record<string, number>;
};

type SpellStepPayload = {
  known?: string[];
  prepared?: string[];
  cantrips?: string[];
};

type StepPayloadMap = {
  ability_scores: AbilityScoreStepPayload;
  origin: OriginStepPayload;
  class: ClassStepPayload;
  proficiencies: ProficiencyStepPayload;
  equipment: EquipmentStepPayload;
  spells: SpellStepPayload;
};

type StepUpdateParams<S extends keyof StepPayloadMap> = {
  draftId: number;
  step: S;
  data: StepPayloadMap[S];
  markComplete?: boolean;
};

export type BuilderStepPayload = StepPayloadMap[keyof StepPayloadMap];

async function fetchDrafts(): Promise<CharacterDraft[]> {
  const response = await api.get<CharacterDraft[]>("/builder/drafts");
  return response.data;
}

export function useCharacterDrafts() {
  return useQuery({
    queryKey: ["character-drafts"],
    queryFn: fetchDrafts,
    staleTime: 1000 * 30
  });
}

async function fetchDraft(draftId: number): Promise<CharacterDraft> {
  const response = await api.get<CharacterDraft>(`/builder/drafts/${draftId}`);
  return response.data;
}

export function useCharacterDraft(draftId?: number) {
  return useQuery({
    queryKey: ["character-draft", draftId],
    queryFn: () => fetchDraft(draftId!),
    enabled: draftId !== undefined
  });
}

async function createDraftRequest(payload: CharacterDraftCreate): Promise<CharacterDraft> {
  const response = await api.post<CharacterDraft>("/builder/drafts", payload);
  return response.data;
}

export function useCreateDraft() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: createDraftRequest,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["character-drafts"] });
      queryClient.invalidateQueries({ queryKey: ["character-draft", data.id] });
    }
  });
}

async function updateDraftStepRequest<S extends keyof StepPayloadMap>({
  draftId,
  step,
  data,
  markComplete
}: StepUpdateParams<S>): Promise<CharacterDraft> {
  const payload: CharacterDraftStepUpdate = {
    payload: data,
    mark_complete: markComplete
  };
  const response = await api.patch<CharacterDraft>(`/builder/drafts/${draftId}/steps/${step}`, payload);
  return response.data;
}

export function useUpdateDraftStep<S extends keyof StepPayloadMap>() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: (params: StepUpdateParams<S>) => updateDraftStepRequest(params),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ["character-drafts"] });
      queryClient.invalidateQueries({ queryKey: ["character-draft", data.id] });
    }
  });
}

async function deleteDraftRequest(draftId: number): Promise<void> {
  await api.delete(`/builder/drafts/${draftId}`);
}

export function useDeleteDraft() {
  const queryClient = useQueryClient();
  return useMutation({
    mutationFn: deleteDraftRequest,
    onSuccess: (_data, draftId) => {
      queryClient.invalidateQueries({ queryKey: ["character-drafts"] });
      queryClient.removeQueries({ queryKey: ["character-draft", draftId] });
    }
  });
}

