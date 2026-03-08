import { useEffect, useMemo, useRef, useState } from "react";
import type { KeyboardEvent } from "react";
import type { Problem } from "../../types/problem";
import ProblemPageCodeEditor from "../ProblemPageCodeEditor/ProblemPageCodeEditor";
import ProblemPageEditorToolbar from "../ProblemPageEditorToolbar/ProblemPageEditorToolbar";
import SplitPane from "../SplitPane/SplitPane";
import {
  completeInterviewSession,
  getInterviewSession,
  postInterviewMessage,
  runSubmission,
  startInterviewSession,
} from "../../services/api";
import type {
  InterviewCompletionResponse,
  InterviewEvaluationResponse,
  InterviewSessionDetailResponse,
} from "../../types/interview";
import "./InterviewPageEditor.css";

interface InterviewPageEditorProps {
  problem: Problem;
}

interface ChatMessage {
  id: string;
  role: "ai" | "you";
  content: string;
  createdAt: number;
}

type InterviewPanelTab = "chat" | "feedback";

export default function InterviewPageEditor({
  problem,
}: InterviewPageEditorProps) {
  const chatMessagesRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);

  const starterCode = problem?.starter_code;
  const languageOptions = useMemo(() => {
    const keys = Object.keys(starterCode);
    return keys.length > 0 ? keys : ["javascript"];
  }, [starterCode]);

  const [selectedLanguage, setSelectedLanguage] = useState(
    languageOptions[0] ?? "javascript"
  );
  const [code, setCode] = useState(starterCode[selectedLanguage] ?? "");
  const [draftMessage, setDraftMessage] = useState("");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [sessionId, setSessionId] = useState<string | null>(null);
  const [sessionStatus, setSessionStatus] = useState<"ACTIVE" | "COMPLETED" | "ABANDONED">(
    "ACTIVE"
  );
  const [canSubmit, setCanSubmit] = useState(false);
  const [activeTab, setActiveTab] = useState<InterviewPanelTab>("chat");
  const [evaluations, setEvaluations] = useState<InterviewEvaluationResponse[]>([]);
  const [completionResult, setCompletionResult] =
    useState<InterviewCompletionResponse | null>(null);
  const [isSending, setIsSending] = useState(false);
  const [isSubmittingCode, setIsSubmittingCode] = useState(false);
  const [isLoadingFeedback, setIsLoadingFeedback] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initializeSession = async () => {
      setError(null);
      setCanSubmit(false);
      setCompletionResult(null);
      setEvaluations([]);
      setActiveTab("chat");
      try {
        const started = await startInterviewSession({ problem_id: problem.id });
        const detail = await getInterviewSession(started.id);
        applySession(detail);
      } catch (sessionError) {
        const message =
          sessionError instanceof Error
            ? sessionError.message
            : "Failed to start interview session.";
        setError(message);
      }
    };

    void initializeSession();
  }, [problem.id]);

  useEffect(() => {
    const container = chatMessagesRef.current;
    if (!container) {
      return;
    }
    container.scrollTop = container.scrollHeight;

    const lastMessage = messages[messages.length - 1];
    if (lastMessage?.role === "ai") {
      inputRef.current?.focus();
    }
  }, [messages]);

  useEffect(() => {
    if (!isSending) {
      return;
    }
    const container = chatMessagesRef.current;
    if (!container) {
      return;
    }
    container.scrollTop = container.scrollHeight;
  }, [isSending]);

  useEffect(() => {
    if (
      sessionStatus !== "COMPLETED" ||
      !sessionId ||
      completionResult ||
      isLoadingFeedback
    ) {
      return;
    }
    const hydrateFeedback = async () => {
      setIsLoadingFeedback(true);
      try {
        const result = await completeInterviewSession(sessionId);
        setCompletionResult(result);
        const detail = await getInterviewSession(sessionId);
        setEvaluations(detail.evaluations ?? []);
      } catch {
        // keep chat functional if completion fails
      } finally {
        setIsLoadingFeedback(false);
      }
    };
    void hydrateFeedback();
  }, [sessionStatus, completionResult, isLoadingFeedback, sessionId]);

  const handleLanguageChange = (nextLanguage: string) => {
    setSelectedLanguage(nextLanguage);
    setCode(starterCode[nextLanguage] ?? "");
  };

  const updateCode = (value: string | undefined) => {
    setCode(value ?? "");
  };

  const handleSend = async () => {
    if (!sessionId) {
      return;
    }
    const content = draftMessage.trim();
    if (!content) {
      return;
    }

    const optimisticMessageId = `optimistic-${Date.now()}`;
    const nextMessages = [
      ...messages,
      {
        id: optimisticMessageId,
        role: "you" as const,
        content,
        createdAt: Date.now(),
      },
    ];
    setMessages(nextMessages);
    setDraftMessage("");
    setIsSending(true);
    setError(null);
    try {
      const detail = await postInterviewMessage(sessionId, {
        content,
        role: "user",
        has_submission: false,
        current_code: code,
        chat_history: toChatHistory(nextMessages),
      });
      applySession(detail);
    } catch (sendError) {
      setMessages((prev) =>
        prev.filter((message) => message.id !== optimisticMessageId)
      );
      setDraftMessage(content);
      const message =
        sendError instanceof Error ? sendError.message : "Failed to send message.";
      setError(message);
    } finally {
      setIsSending(false);
    }
  };

  const handleSubmitCode = async () => {
    if (!sessionId) {
      return;
    }

    setIsSubmittingCode(true);
    setError(null);

    try {
      const submission = await runSubmission({
        problem_id: problem.id,
        code_submitted: code,
        language: selectedLanguage,
      });

      const submissionSummary =
        submission.result === "pass"
          ? `I submitted my ${selectedLanguage} solution and all tests passed.`
          : `I submitted my ${selectedLanguage} solution and it failed. Error: ${
              submission.error ?? "Unknown failure"
            }`;

      const nextMessages = [
        ...messages,
        {
          id: `submission-${Date.now()}`,
          role: "you" as const,
          content: submissionSummary,
          createdAt: Date.now(),
        },
      ];
      const detail = await postInterviewMessage(sessionId, {
        content: submissionSummary,
        role: "user",
        has_submission: true,
        current_code: code,
        chat_history: toChatHistory(nextMessages),
      });
      applySession(detail);
    } catch (submitError) {
      const message =
        submitError instanceof Error
          ? submitError.message
          : "Failed to submit code.";
      setError(message);
    } finally {
      setIsSubmittingCode(false);
    }
  };

  const handleDraftKeyDown = (event: KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key === "Enter" && !event.shiftKey) {
      event.preventDefault();
      void handleSend();
    }
  };

  const applySession = (detail: InterviewSessionDetailResponse) => {
    setSessionId(detail.id);
    setSessionStatus(detail.status);
    setEvaluations(detail.evaluations ?? []);
    const nextCanSubmit = canSubmit || Boolean(detail.can_code);
    setCanSubmit(nextCanSubmit);
    if (detail.status === "COMPLETED") {
      setActiveTab("feedback");
    }
    setMessages(
      sortMessagesByTime(
        detail.messages
          .filter(
            (message) => message.role === "assistant" || message.role === "user"
          )
          .map((message) => ({
            id: message.id,
            role: message.role === "assistant" ? "ai" : "you",
            content: message.content,
            createdAt: new Date(message.created_at).getTime(),
          }))
      )
    );
  };

  const rubricRows = useMemo(() => summarizeRubric(evaluations), [evaluations]);
  const aiAdditionalImprovements = useMemo(
    () => extractAiAdditionalImprovements(evaluations),
    [evaluations]
  );
  const nitpicks = useMemo(
    () =>
      aiAdditionalImprovements.length > 0
        ? aiAdditionalImprovements
        : buildNitpicks(rubricRows, completionResult),
    [aiAdditionalImprovements, rubricRows, completionResult]
  );
  const finalScore = completionResult?.final_score ?? null;
  const didPass = finalScore !== null ? finalScore >= 30 : null;

  return (
    <div className="interview-editor-shell">
      <SplitPane
        orientation="vertical"
        defaultPrimarySize={66}
        minPrimarySize={46}
        maxPrimarySize={84}
        className="interview-inner-split"
        primary={
          <section className="editor-panel editor-panel-active" aria-label="Code editor">
            <ProblemPageEditorToolbar
              selectedLanguage={selectedLanguage}
              handleLanguageChange={handleLanguageChange}
              languageOptions={languageOptions}
              onSubmit={handleSubmitCode}
              isSubmitting={isSubmittingCode}
              isSubmitDisabled={!canSubmit}
              submitLabel="Submit Code"
              submittingLabel="Submitting..."
            />
            <ProblemPageCodeEditor
              selectedLanguage={selectedLanguage}
              updateCode={updateCode}
              code={code}
              readOnly={false}
              className="editor-shell-active"
            />
          </section>
        }
        secondary={
          <section className="interview-chat-panel" aria-label="AI interview panel">
            <header className="interview-chat-header">
              <span>AI Interview Panel</span>
            </header>
            <div className="interview-panel-tabs" role="tablist" aria-label="Interview tabs">
              <button
                type="button"
                role="tab"
                aria-selected={activeTab === "chat"}
                className={`interview-tab ${activeTab === "chat" ? "active" : ""}`}
                onClick={() => setActiveTab("chat")}
              >
                Chat
              </button>
              <button
                type="button"
                role="tab"
                aria-selected={activeTab === "feedback"}
                className={`interview-tab ${activeTab === "feedback" ? "active" : ""}`}
                onClick={() => {
                  if (sessionStatus === "COMPLETED") {
                    setActiveTab("feedback");
                  }
                }}
                disabled={sessionStatus !== "COMPLETED"}
              >
                Feedback
              </button>
            </div>
            {activeTab === "chat" ? (
              <>
                <div className="interview-chat-messages" ref={chatMessagesRef}>
                  {messages.length === 0 && (
                    <p className="interview-chat-empty">
                      Interview messages will appear here when the session starts.
                    </p>
                  )}
                  {messages.map((message) => (
                    <article
                      key={message.id}
                      className={`chat-bubble ${message.role === "ai" ? "ai" : "you"}`}
                    >
                      <p className="chat-bubble-role">
                        {message.role === "ai" ? "Interviewer" : "You"}
                      </p>
                      <p>{message.content}</p>
                    </article>
                  ))}
                </div>
                <footer className="interview-chat-input-wrap">
                  <textarea
                    ref={inputRef}
                    value={draftMessage}
                    onChange={(event) => setDraftMessage(event.target.value)}
                    onKeyDown={handleDraftKeyDown}
                    placeholder="Explain your thinking, ask a clarification, or answer a follow-up..."
                    rows={3}
                  />
                  <button
                    type="button"
                    onClick={handleSend}
                    disabled={
                      isSending ||
                      isSubmittingCode ||
                      !sessionId ||
                      !draftMessage.trim()
                    }
                  >
                    {isSending ? "Sending..." : "Send"}
                  </button>
                </footer>
              </>
            ) : (
              <div className="interview-feedback-panel">
                {isLoadingFeedback && (
                  <div className="feedback-loading" role="status" aria-live="polite">
                    <span className="feedback-spinner" aria-hidden="true" />
                    <span>Generating feedback...</span>
                  </div>
                )}
                {completionResult && (
                  <div className="score-card">
                    <h4>Final Result</h4>
                    <p className="score-line">
                      Score: <strong>{(finalScore ?? 0).toFixed(2)} / 50.00</strong>
                    </p>
                    <p
                      className={`pass-fail-pill ${
                        didPass ? "pass-fail-pass" : "pass-fail-fail"
                      }`}
                    >
                      {didPass ? "Pass" : "Fail"}
                    </p>
                  </div>
                )}
                <h3>Rubric</h3>
                {rubricRows.length === 0 && (
                  <p className="interview-chat-empty">
                    Feedback will appear here once the interview has enough signal.
                  </p>
                )}
                {rubricRows.length > 0 && (
                  <div className="rubric-table">
                    {rubricRows.map((row) => (
                      <div key={row.label} className="rubric-row">
                        <span>{row.label}</span>
                        <span>{row.value.toFixed(2)} / 10.00</span>
                      </div>
                    ))}
                  </div>
                )}
                {completionResult && (
                  <div className="feedback-block">
                    <h4>Summary</h4>
                    <ul className="feedback-list">
                      {completionResult.strengths.map((item) => (
                        <li key={`strength-${item}`}>{item}</li>
                      ))}
                    </ul>
                    <ul className="feedback-list">
                      {completionResult.gaps.map((item) => (
                        <li key={`gap-${item}`}>{item}</li>
                      ))}
                    </ul>
                  </div>
                )}
                <div className="feedback-block">
                  <h4>Additional Improvements</h4>
                  <ul className="feedback-list">
                    {nitpicks.map((item) => (
                      <li key={item}>{item}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
            {error && <p className="interview-chat-error">{error}</p>}
          </section>
        }
      />
    </div>
  );
}

function sortMessagesByTime(messages: ChatMessage[]): ChatMessage[] {
  return [...messages].sort((a, b) => {
    if (a.createdAt !== b.createdAt) {
      return a.createdAt - b.createdAt;
    }
    return a.id.localeCompare(b.id);
  });
}

function toChatHistory(
  messages: ChatMessage[]
): Array<{ role: "user" | "assistant"; content: string }> {
  return messages.map((message) => ({
    role: message.role === "ai" ? "assistant" : "user",
    content: message.content,
  }));
}

function summarizeRubric(evaluations: InterviewEvaluationResponse[]) {
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

function buildNitpicks(
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

function extractAiAdditionalImprovements(
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
