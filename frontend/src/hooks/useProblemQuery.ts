import { useQuery } from "@tanstack/react-query";
import { getProblemById } from "../services/api";

export function useProblemQuery(problemId: string) {
  const fetchProblemById = () => getProblemById(problemId);
  return useQuery({
    queryKey: ["problem", problemId],
    queryFn: fetchProblemById,
    enabled: Boolean(problemId),
    retry: 1,
    refetchOnWindowFocus: false,
  });
}
