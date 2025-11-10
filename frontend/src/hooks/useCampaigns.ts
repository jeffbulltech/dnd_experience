import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { api } from "../services/api";
import { Campaign } from "../types";

async function fetchCampaigns(): Promise<Campaign[]> {
  const response = await api.get<Campaign[]>("/campaigns");
  return response.data;
}

export function useCampaigns() {
  return useQuery({
    queryKey: ["campaigns"],
    queryFn: () => fetchCampaigns(),
    staleTime: 1000 * 60
  });
}

type CreateCampaignPayload = {
  name: string;
  description?: string | null;
};

async function createCampaignRequest(payload: CreateCampaignPayload): Promise<Campaign> {
  const response = await api.post<Campaign>("/campaigns", payload);
  return response.data;
}

export function useCreateCampaign() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: createCampaignRequest,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["campaigns"] });
    }
  });
}

