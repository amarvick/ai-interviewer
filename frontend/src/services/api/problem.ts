import type {
  Problem,
  ProblemList,
  ProblemListProblemsResponse,
} from "../../types/problem";
import { API_BASE_URL, parseJson } from "./api";
import { getAuthToken } from "../auth";

function authHeaders(): HeadersInit {
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function getProblemLists(): Promise<ProblemList[]> {
  const response = await fetch(`${API_BASE_URL}/problem-lists`);
  return parseJson<ProblemList[]>(response);
}

export async function getProblemsByProblemListId(
  problemListId: string
): Promise<ProblemListProblemsResponse> {
  const response = await fetch(`${API_BASE_URL}/problems/${problemListId}`, {
    headers: {
      ...authHeaders(),
    },
  });
  return parseJson<ProblemListProblemsResponse>(response);
}

export async function getProblemById(problemId: string): Promise<Problem> {
  const response = await fetch(`${API_BASE_URL}/problem/${problemId}`);
  return parseJson<Problem>(response);
}
