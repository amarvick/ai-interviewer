export interface SubmissionPayload {
  problem_id: string;
  code_submitted: string;
  language: string;
}

export interface SubmissionResponse {
  id: number;
  user_id: number;
  problem_id: string;
  code_submitted: string;
  language: string;
  result: "pass" | "fail";
  error?: string | null;
  created_at?: string;
}
