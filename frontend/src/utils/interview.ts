import type { InterviewCompletionResponse, InterviewEvaluationResponse } from "../types/interview";

export interface ChatMessage {
  id: string;
  role: "ai" | "you";
  content: string;
  createdAt: number;
}

export function sortMessagesByTime(messages: ChatMessage[]): ChatMessage[] {
  return [...messages].sort((a, b) => {
    if (a.createdAt !== b.createdAt) {
      return a.createdAt - b.createdAt;
    }
    return a.id.localeCompare(b.id);
  });
}

export function toChatHistory(
  messages: ChatMessage[]
): Array<{ role: "user" | "assistant"; content: string }> {
  return messages.map((message) => ({
    role: message.role === "ai" ? "assistant" : "user",
    content: message.content,
  }));
}

export function summarizeRubric(evaluations: InterviewEvaluationResponse[]) {
  if (!evaluations.length) {
    return [];
  }
  const totals = {
    problem_understanding: 0,
    approach_quality: 0,
    correctness_reasoning: 0,
    complexity_analysis: 0,
    communication_clarity: 0,
  };
  for (const evalItem of evaluations) {
    totals.problem_understanding += evalItem.problem_understanding_score;
    totals.approach_quality += evalItem.approach_quality_score;
    totals.correctness_reasoning += evalItem.code_correctness_reasoning_score;
    totals.complexity_analysis += evalItem.complexity_analysis_score;
    totals.communication_clarity += evalItem.communication_clarity_score;
  }
  const count = evaluations.length;
  return [
    {
      label: "Problem Understanding",
      value: totals.problem_understanding / count,
    },
    {
      label: "Approach Quality",
      value: totals.approach_quality / count,
    },
    {
      label: "Correctness Reasoning",
      value: totals.correctness_reasoning / count,
    },
    {
      label: "Complexity Analysis",
      value: totals.complexity_analysis / count,
    },
    {
      label: "Communication Clarity",
      value: totals.communication_clarity / count,
    },
  ];
}

export function buildNitpicks(
  rubricRows: Array<{ label: string; value: number }>,
  completionResult: InterviewCompletionResponse | null
): string[] {
  const nits: string[] = [];
  const weakest = [...rubricRows].sort((a, b) => a.value - b.value).slice(0, 2);
  for (const row of weakest) {
    if (row.label === "Complexity Analysis") {
      nits.push(
        "Quantify complexity per operation, not just final Big-O, to strengthen rigor."
      );
    } else if (row.label === "Communication Clarity") {
      nits.push("Use short structured answers: plan, invariant, complexity, tradeoff.");
    } else if (row.label === "Correctness Reasoning") {
      nits.push("Narrate one complete dry run with indices/variables after coding.");
    } else if (row.label === "Approach Quality") {
      nits.push("Mention one rejected alternative and why your chosen method is better.");
    } else if (row.label === "Problem Understanding") {
      nits.push(
        "State assumptions and edge cases explicitly before implementation begins."
      );
    }
  }
  if (completionResult?.next_steps?.length) {
    nits.push(...completionResult.next_steps.slice(0, 2));
  }
  if (!nits.length) {
    nits.push("Keep explaining invariants while coding to reduce logical slips.");
    nits.push("Summarize final tradeoffs in one sentence before submission.");
  }
  return Array.from(new Set(nits));
}

export function extractAiAdditionalImprovements(
  evaluations: InterviewEvaluationResponse[]
): string[] {
  const ordered = [...evaluations].sort(
    (a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime()
  );
  for (const evaluation of ordered) {
    const raw = (evaluation.rubric_json ?? {}) as Record<string, unknown>;
    const candidate = raw.additional_improvements;
    if (!Array.isArray(candidate)) {
      continue;
    }
    const normalized = candidate
      .map((item) => String(item).trim())
      .filter((item) => item.length > 0)
      .slice(0, 6);
    if (normalized.length > 0) {
      return normalized;
    }
  }
  return [];
}
