import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../services/api";
import { Character } from "../types";

type CharacterFilters = {
  campaignId?: number;
};

async function fetchCharacters(filters: CharacterFilters): Promise<Character[]> {
  const response = await api.get<Character[]>("/characters", {
    params: {
      campaign_id: filters.campaignId
    }
  });
  return response.data;
}

type CreateCharacterPayload = {
  name: string;
  level?: number;
  race?: string | null;
  character_class?: string | null;
  background?: string | null;
  campaign_id?: number | null;
};

async function createCharacterRequest(payload: CreateCharacterPayload): Promise<Character> {
  const response = await api.post<Character>("/characters", payload);
  return response.data;
}

export function useCharacters(filters: CharacterFilters = {}) {
  return useQuery({
    queryKey: ["characters", filters],
    queryFn: () => fetchCharacters(filters),
    staleTime: 1000 * 30
  });
}

export function useCreateCharacter() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createCharacterRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["characters"], exact: false });
    }
  });
}

type UpdateCharacterPayload = {
  id: number;
  updates: Partial<Character>;
};

async function updateCharacterRequest({ id, updates }: UpdateCharacterPayload): Promise<Character> {
  const response = await api.put<Character>(`/characters/${id}`, updates);
  return response.data;
}

export function useUpdateCharacter() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: updateCharacterRequest,
    onSuccess: () => {
      // Invalidate all character queries to refresh both campaign and all-user character lists
      queryClient.invalidateQueries({ queryKey: ["characters"], exact: false });
      queryClient.refetchQueries({ queryKey: ["characters"], exact: false });
    }
  });
}

