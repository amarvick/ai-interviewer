import { useMemo, useState } from "react";
import "./ProblemPageTerminal.css";
import type { TestCase } from "../types/testcase";
import type { SubmissionResponse } from "../types/submission";

type TestCaseStatus = "pending" | "pass" | "fail";

interface ProblemPageTerminalProps {
  testCases: TestCase[];
  testCaseStatuses: Record<number, TestCaseStatus>;
  submissions: SubmissionResponse[];
  hasSubmittedInSession: boolean;
  sessionErrors: string[];
}

function prettyJson(value: unknown): string {
  try {
    return JSON.stringify(value);
  } catch {
    return String(value);
  }
}

export default function ProblemPageTerminal({
  testCases,
  testCaseStatuses,
  submissions,
  hasSubmittedInSession,
  sessionErrors,
}: ProblemPageTerminalProps) {
  const [activeTab, setActiveTab] = useState<"results" | "submissions">(
    "results"
  );
  const orderedSubmissions = useMemo(
    () =>
      [...submissions].sort((a, b) => {
        const aTime = a.created_at ? new Date(a.created_at).getTime() : 0;
        const bTime = b.created_at ? new Date(b.created_at).getTime() : 0;
        return bTime - aTime;
      }),
    [submissions]
  );

  return (
    <section className="terminal-panel" aria-label="Submission and results panel">
      <header className="terminal-header">
        <div className="terminal-tabs">
          <button
            type="button"
            className={activeTab === "results" ? "tab-button active" : "tab-button"}
            onClick={() => setActiveTab("results")}
          >
            Test Results
          </button>
          <button
            type="button"
            className={
              activeTab === "submissions" ? "tab-button active" : "tab-button"
            }
            onClick={() => setActiveTab("submissions")}
          >
            Submissions
          </button>
        </div>
      </header>

      <div className="terminal-output">
        {activeTab === "results" && (
          <div className="terminal-list">
            {!hasSubmittedInSession && (
              <p className="terminal-empty">You must run your code first</p>
            )}

            {hasSubmittedInSession &&
              testCases.map((testCase, index) => {
                const status = testCaseStatuses[testCase.id] ?? "pending";
                return (
                  <article key={testCase.id} className="terminal-item">
                    <div className="terminal-item-title">
                      <span className={`status-dot ${status}`} />
                      <strong>Case {index + 1}</strong>
                    </div>
                    <div className="terminal-item-meta">
                      <span>Input: {prettyJson(testCase.params)}</span>
                      <span>Expected: {prettyJson(testCase.expected_output)}</span>
                    </div>
                  </article>
                );
              })}

            {hasSubmittedInSession && sessionErrors.length > 0 && (
              <article className="terminal-item terminal-item-error">
                <div className="terminal-item-title">
                  <strong>Errors</strong>
                </div>
                <div className="terminal-item-meta">
                  {sessionErrors.map((error, index) => (
                    <span key={`${error}-${index}`}>{error}</span>
                  ))}
                </div>
              </article>
            )}
          </div>
        )}

        {activeTab === "submissions" && (
          <div className="terminal-list">
            {orderedSubmissions.map((submission) => (
              <article key={submission.id} className="terminal-item">
                <div className="terminal-item-title">
                  <span
                    className={`status-dot ${
                      submission.result === "pass" ? "pass" : "fail"
                    }`}
                  />
                  <strong>Submission #{submission.id}</strong>
                </div>
                <div className="terminal-item-meta">
                  <span>
                    Date:{" "}
                    {submission.created_at
                      ? new Date(submission.created_at).toLocaleString()
                      : "Unavailable"}
                  </span>
                  <span>Language: {submission.language}</span>
                  <span>Result: {submission.result.toUpperCase()}</span>
                </div>
              </article>
            ))}
            {orderedSubmissions.length === 0 && (
              <p className="terminal-empty">No submissions yet.</p>
            )}
          </div>
        )}
      </div>
    </section>
  );
}
