import { useQuery } from "@tanstack/react-query";
import { getProblemsByProblemListId } from "../services/api";

export function useProblemsQuery(problemListId: string) {
  const getProblemsById = () => getProblemsByProblemListId(problemListId);
  return useQuery({
    queryKey: ["problems", problemListId],
    queryFn: getProblemsById,
    enabled: Boolean(problemListId),
    retry: 1,
    refetchOnWindowFocus: false,
  });
}
