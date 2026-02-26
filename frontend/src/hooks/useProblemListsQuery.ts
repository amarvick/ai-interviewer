import { useQuery } from "@tanstack/react-query";
import { getProblemLists } from "../services/api";

export function useProblemListsQuery(enabled = true) {
  return useQuery({
    queryKey: ["problem-lists"],
    queryFn: getProblemLists,
    enabled,
    retry: 1,
    refetchOnWindowFocus: false,
  });
}
