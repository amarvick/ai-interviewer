export interface SubmissionPayload {
  problem_id: number;
  code: string;
  language: string;
}

export interface SubmissionResponse {
  result: "pass" | "fail";
  feedback: string;
}
