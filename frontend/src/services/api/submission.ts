import type {
  SubmissionPayload,
  SubmissionResponse,
} from "../../types/submission";
import { API_BASE_URL, parseJson } from "./api";
import { getAuthToken } from "../auth";

function authHeaders(): HeadersInit {
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function runSubmission(
  payload: SubmissionPayload
): Promise<SubmissionResponse> {
  const response = await fetch(`${API_BASE_URL}/submission/submit`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify(payload),
  });

  return parseJson<SubmissionResponse>(response);
}

export async function getSubmissions(
  problemId: string
): Promise<SubmissionResponse[]> {
  const response = await fetch(
    `${API_BASE_URL}/submissions?problem_id=${encodeURIComponent(problemId)}`,
    {
      headers: {
        ...authHeaders(),
      },
    }
  );

  return parseJson<SubmissionResponse[]>(response);
}
