import type {
  Problem,
  ProblemList,
  ProblemListProblemsResponse,
} from "../types/problem";
import type {
  LoginPayload,
  SignupPayload,
  TokenResponse,
  User,
} from "../types/user";

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

async function parseJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const fallback = `Request failed with status ${response.status}`;
    try {
      const errorPayload = (await response.json()) as { detail?: string };
      throw new Error(errorPayload.detail ?? fallback);
    } catch {
      throw new Error(fallback);
    }
  }

  return (await response.json()) as T;
}

export async function getProblemLists(): Promise<ProblemList[]> {
  const response = await fetch(`${API_BASE_URL}/problem-lists`);
  return parseJson<ProblemList[]>(response);
}

export async function getProblemsByProblemListId(
  problemListId: string
): Promise<ProblemListProblemsResponse> {
  const response = await fetch(`${API_BASE_URL}/problems/${problemListId}`);
  return parseJson<ProblemListProblemsResponse>(response);
}

export async function getProblemById(
  problemId: string
): Promise<Problem> {
  const response = await fetch(`${API_BASE_URL}/problem/${problemId}`);
  return parseJson<Problem>(response);
}

export async function login(payload: LoginPayload): Promise<TokenResponse> {
  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return parseJson<TokenResponse>(response);
}

export async function register(payload: SignupPayload): Promise<User> {
  const response = await fetch(`${API_BASE_URL}/auth/register`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return parseJson<User>(response);
}
