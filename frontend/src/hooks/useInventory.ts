import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../services/api";
import { InventoryItem } from "../types";

type InventoryFilters = {
  characterId?: number;
};

async function fetchInventory(filters: InventoryFilters): Promise<InventoryItem[]> {
  const response = await api.get<InventoryItem[]>("/inventory", {
    params: { character_id: filters.characterId }
  });
  return response.data;
}

type InventoryCreatePayload = {
  character_id: number;
  name: string;
  quantity?: number;
  weight?: number | null;
  description?: string | null;
  properties?: Record<string, unknown> | null;
};

type InventoryUpdatePayload = {
  id: number;
  updates: Partial<Omit<InventoryCreatePayload, "character_id">>;
};

export function useInventory(filters: InventoryFilters = {}) {
  return useQuery({
    queryKey: ["inventory", filters],
    queryFn: () => fetchInventory(filters),
    enabled: Boolean(filters.characterId),
    staleTime: 1000 * 30
  });
}

export function useInventoryMutations(characterId?: number) {
  const queryClient = useQueryClient();

  const invalidate = () =>
    queryClient.invalidateQueries({
      queryKey: ["inventory"],
      exact: false
    });

  const createItem = useMutation({
    mutationFn: (payload: InventoryCreatePayload) => api.post<InventoryItem>("/inventory", payload).then((res) => res.data),
    onSuccess: () => invalidate()
  });

  const updateItem = useMutation({
    mutationFn: ({ id, updates }: InventoryUpdatePayload) =>
      api.put<InventoryItem>(`/inventory/${id}`, updates).then((res) => res.data),
    onSuccess: () => invalidate()
  });

  const deleteItem = useMutation({
    mutationFn: (itemId: number) => api.delete(`/inventory/${itemId}`),
    onSuccess: () => invalidate()
  });

  return {
    createItem,
    updateItem,
    deleteItem
  };
}

