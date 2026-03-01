import type {
  InterviewCompletionResponse,
  InterviewMessagePayload,
  InterviewSessionDetailResponse,
  InterviewSessionResponse,
  StartInterviewSessionPayload,
} from "../../types/interview";
import { API_BASE_URL, parseJson } from "./api";
import { getAuthToken } from "../auth";

function authHeaders(): HeadersInit {
  const token = getAuthToken();
  return token ? { Authorization: `Bearer ${token}` } : {};
}

export async function startInterviewSession(
  payload: StartInterviewSessionPayload
): Promise<InterviewSessionResponse> {
  const response = await fetch(`${API_BASE_URL}/interview/session/start`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...authHeaders(),
    },
    body: JSON.stringify(payload),
  });
  return parseJson<InterviewSessionResponse>(response);
}

export async function getInterviewSession(
  sessionId: string
): Promise<InterviewSessionDetailResponse> {
  const response = await fetch(`${API_BASE_URL}/interview/session/${sessionId}`, {
    headers: {
      ...authHeaders(),
    },
  });
  return parseJson<InterviewSessionDetailResponse>(response);
}

export async function postInterviewMessage(
  sessionId: string,
  payload: InterviewMessagePayload
): Promise<InterviewSessionDetailResponse> {
  const response = await fetch(
    `${API_BASE_URL}/interview/session/${sessionId}/message`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(),
      },
      body: JSON.stringify(payload),
    }
  );
  return parseJson<InterviewSessionDetailResponse>(response);
}

export async function completeInterviewSession(
  sessionId: string,
  finalScore?: number
): Promise<InterviewCompletionResponse> {
  const response = await fetch(
    `${API_BASE_URL}/interview/session/${sessionId}/complete`,
    {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        ...authHeaders(),
      },
      body: JSON.stringify({ final_score: finalScore ?? null }),
    }
  );
  return parseJson<InterviewCompletionResponse>(response);
}
