import { useQuery } from "@tanstack/react-query";
import { getProblems } from "../services/api";

export function useProblemsQuery(problemListId: string) {
  const getProblemsById = () => getProblems(problemListId);
  return useQuery({
    queryKey: ["problems", problemListId],
    queryFn: getProblemsById,
    retry: 1,
    refetchOnWindowFocus: false,
  });
}
