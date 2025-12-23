import { useQuery } from "@tanstack/react-query";

import { api } from "../services/api";

export type AdventureTemplate = {
  id: string;
  name: string;
  description: string;
  level_range: string;
  setting: string;
};

async function fetchAdventures(): Promise<AdventureTemplate[]> {
  const response = await api.get<AdventureTemplate[]>("/adventures");
  return response.data;
}

export function useAdventures() {
  return useQuery({
    queryKey: ["adventures"],
    queryFn: fetchAdventures,
    staleTime: 5 * 60 * 1000, // 5 minutes
  });
}
