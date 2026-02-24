import type {
  SubmissionPayload,
  SubmissionResponse,
} from "../../types/submission";
import { API_BASE_URL, parseJson } from "./api";

export async function runSubmission(
  payload: SubmissionPayload
): Promise<SubmissionResponse> {
  const response = await fetch(`${API_BASE_URL}/submission/submit`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify(payload),
  });

  return parseJson<SubmissionResponse>(response);
}
