import { useQuery } from "@tanstack/react-query";
import { getProblemLists } from "../services/api";

export function useProblemListsQuery() {
  return useQuery({
    queryKey: ["problem-lists"],
    queryFn: getProblemLists,
    retry: 1,
    refetchOnWindowFocus: false,
  });
}
