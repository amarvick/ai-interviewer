import type { SubmissionResponse } from "../types/submission";
import type { Problem } from "../types/problem";

export type TestCaseStatus = "pending" | "pass" | "fail";

export function buildInitialStatuses(
  problem: Problem
): Record<string, TestCaseStatus> {
  return problem.test_cases.reduce<Record<string, TestCaseStatus>>(
    (acc, testCase) => {
      acc[testCase.id] = "pending";
      return acc;
    },
    {}
  );
}

export function parseFailedCaseIndex(errorText?: string | null): number | null {
  if (!errorText) {
    return null;
  }
  const match = errorText.match(/test case #(\d+)/i);
  if (!match) {
    return null;
  }
  const parsed = Number(match[1]);
  return Number.isInteger(parsed) && parsed > 0 ? parsed : null;
}

export function mapStatusesForResult(
  prev: Record<string, TestCaseStatus>,
  problem: Problem,
  submission: SubmissionResponse
): Record<string, TestCaseStatus> {
  if (submission.result === "pass") {
    return Object.fromEntries(
      Object.keys(prev).map((id) => [id, "pass"])
    ) as Record<string, TestCaseStatus>;
  }

  const next = Object.fromEntries(
    Object.keys(prev).map((id) => [id, "pending"])
  ) as Record<string, TestCaseStatus>;

  const failedIndex = parseFailedCaseIndex(submission.error);
  if (failedIndex === null) {
    return next;
  }

  const orderedIds = problem.test_cases.map((testCase) => testCase.id);
  for (let i = 0; i < orderedIds.length; i += 1) {
    const id = orderedIds[i];
    if (i + 1 < failedIndex) {
      next[id] = "pass";
    } else if (i + 1 === failedIndex) {
      next[id] = "fail";
    }
  }
  return next;
}
