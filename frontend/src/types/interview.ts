export type InterviewStage =
  | "INTRO"
  | "CLARIFICATION"
  | "APPROACH_DISCUSSION"
  | "PSEUDOCODE"
  | "CODING"
  | "COMPLEXITY_DISCUSSION"
  | "FOLLOW_UP"
  | "FEEDBACK"
  | "COMPLETE";

export type InterviewRole = "system" | "assistant" | "user";
export type InterviewSessionStatus = "ACTIVE" | "COMPLETED" | "ABANDONED";

export interface InterviewSessionResponse {
  id: string;
  user_id: string;
  problem_id: string;
  stage: InterviewStage;
  status: InterviewSessionStatus;
  final_score?: number | null;
  stuck_signal_count: number;
  nudges_used_in_stage: number;
  started_at: string;
  completed_at?: string | null;
  created_at: string;
  updated_at: string;
}

export interface InterviewMessageResponse {
  id: string;
  session_id: string;
  user_id?: string | null;
  role: InterviewRole;
  content: string;
  stage_at_message: InterviewStage;
  created_at: string;
}

export interface InterviewEvaluationResponse {
  id: string;
  session_id: string;
  stage: InterviewStage;
  problem_understanding_score: number;
  approach_quality_score: number;
  code_correctness_reasoning_score: number;
  complexity_analysis_score: number;
  communication_clarity_score: number;
  total_score: number;
  passed: boolean;
  summary?: string | null;
  rubric_json?: Record<string, unknown>;
  created_at: string;
}

export interface InterviewSessionDetailResponse extends InterviewSessionResponse {
  messages: InterviewMessageResponse[];
  evaluations: InterviewEvaluationResponse[];
  can_code?: boolean;
}

export interface InterviewCompletionResponse extends InterviewSessionResponse {
  strengths: string[];
  gaps: string[];
  next_steps: string[];
}

export interface StartInterviewSessionPayload {
  problem_id: string;
}

export interface InterviewMessagePayload {
  content: string;
  role?: "user";
  has_submission?: boolean;
  current_code?: string;
  chat_history?: Array<{ role: "user" | "assistant"; content: string }>;
}
