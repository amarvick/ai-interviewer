import { useEffect, useMemo, useState } from "react";
import type { KeyboardEvent } from "react";
import type { Problem } from "../../types/problem";
import ProblemPageCodeEditor from "../ProblemPageCodeEditor/ProblemPageCodeEditor";
import ProblemPageEditorToolbar from "../ProblemPageEditorToolbar/ProblemPageEditorToolbar";
import {
  completeInterviewSession,
  getInterviewSession,
  postInterviewMessage,
  runSubmission,
  startInterviewSession,
} from "../../services/api";
import type {
  InterviewCompletionResponse,
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
}

type InterviewPanelTab = "chat" | "results";

export default function InterviewPageEditor({
  problem,
}: InterviewPageEditorProps) {
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
  const [sessionStage, setSessionStage] = useState<string>("INTRO");
  const [sessionStatus, setSessionStatus] = useState<string>("ACTIVE");
  const [isSending, setIsSending] = useState(false);
  const [isSubmittingCode, setIsSubmittingCode] = useState(false);
  const [isCompleting, setIsCompleting] = useState(false);
  const [activeTab, setActiveTab] = useState<InterviewPanelTab>("chat");
  const [completionResult, setCompletionResult] =
    useState<InterviewCompletionResponse | null>(null);
  const [evaluationSummaries, setEvaluationSummaries] = useState<string[]>([]);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initializeSession = async () => {
      setError(null);
      setCompletionResult(null);
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
    setMessages((prev) => [
      ...prev,
      { id: optimisticMessageId, role: "you", content },
    ]);
    setDraftMessage("");
    setIsSending(true);
    setError(null);
    try {
      const detail = await postInterviewMessage(sessionId, {
        content,
        role: "user",
        has_submission: false,
        current_code: code,
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

      const detail = await postInterviewMessage(sessionId, {
        content: submissionSummary,
        role: "user",
        has_submission: true,
        current_code: code,
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

  const handleCompleteInterview = async () => {
    if (!sessionId) {
      return;
    }
    setIsCompleting(true);
    setError(null);
    try {
      const result = await completeInterviewSession(sessionId);
      setCompletionResult(result);
      setSessionStage(result.stage);
      setSessionStatus(result.status);
      setActiveTab("results");
    } catch (completeError) {
      const message =
        completeError instanceof Error
          ? completeError.message
          : "Failed to complete interview.";
      setError(message);
    } finally {
      setIsCompleting(false);
    }
  };

  const applySession = (detail: InterviewSessionDetailResponse) => {
    setSessionId(detail.id);
    setSessionStage(detail.stage);
    setSessionStatus(detail.status);
    setEvaluationSummaries(
      detail.evaluations
        .slice()
        .reverse()
        .map((evaluation) => `${evaluation.stage}: ${evaluation.summary ?? "No summary"}`)
    );
    setMessages(
      detail.messages
        .filter((message) => message.role === "assistant" || message.role === "user")
        .map((message) => ({
          id: message.id,
          role: message.role === "assistant" ? "ai" : "you",
          content: message.content,
        }))
    );
  };

  return (
    <div className="interview-editor-stack">
      <section className="editor-panel" aria-label="Code editor">
        <ProblemPageEditorToolbar
          selectedLanguage={selectedLanguage}
          handleLanguageChange={handleLanguageChange}
          languageOptions={languageOptions}
          onSubmit={handleSubmitCode}
          isSubmitting={isSubmittingCode}
          submitLabel="Submit Code"
          submittingLabel="Submitting..."
        />
        <ProblemPageCodeEditor
          selectedLanguage={selectedLanguage}
          updateCode={updateCode}
          code={code}
        />
      </section>

      <section className="interview-chat-panel" aria-label="AI interview panel">
        <header className="interview-chat-header">
          <span>AI Interview Panel</span>
          <div className="interview-chat-header-right">
            <span className="stage-pill">{sessionStage}</span>
            <span className="stage-pill status-pill">{sessionStatus}</span>
          </div>
        </header>
        <div className="interview-panel-tabs" role="tablist" aria-label="Interview panel tabs">
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
            aria-selected={activeTab === "results"}
            className={`interview-tab ${activeTab === "results" ? "active" : ""}`}
            onClick={() => setActiveTab("results")}
          >
            Results
          </button>
        </div>
        {activeTab === "chat" ? (
          <>
            <div className="interview-chat-messages">
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
                  isSending || isSubmittingCode || !sessionId || !draftMessage.trim()
                }
              >
                {isSending ? "Sending..." : "Send"}
              </button>
            </footer>
          </>
        ) : (
          <div className="interview-results-panel">
            <div className="interview-results-actions">
              <button
                type="button"
                onClick={handleCompleteInterview}
                disabled={!sessionId || isCompleting || sessionStatus === "COMPLETED"}
              >
                {isCompleting
                  ? "Calculating..."
                  : sessionStatus === "COMPLETED"
                    ? "Interview Completed"
                    : "Finish Interview"}
              </button>
            </div>
            {!completionResult && (
              <p className="interview-chat-empty">
                Finish the interview to see your final results and feedback.
              </p>
            )}
            {completionResult && (
              <div className="interview-results-content">
                <p>
                  <strong>Final Score:</strong> {completionResult.final_score ?? 0}/10
                </p>
                <div>
                  <p className="results-heading">Strengths</p>
                  <ul className="results-list">
                    {completionResult.strengths.map((item) => (
                      <li key={`strength-${item}`}>{item}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="results-heading">Gaps</p>
                  <ul className="results-list">
                    {completionResult.gaps.map((item) => (
                      <li key={`gap-${item}`}>{item}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <p className="results-heading">Next Steps</p>
                  <ul className="results-list">
                    {completionResult.next_steps.map((item) => (
                      <li key={`next-${item}`}>{item}</li>
                    ))}
                  </ul>
                </div>
              </div>
            )}
            {evaluationSummaries.length > 0 && (
              <div className="interview-results-history">
                <p className="results-heading">Stage Summaries</p>
                <ul className="results-list">
                  {evaluationSummaries.map((summary) => (
                    <li key={summary}>{summary}</li>
                  ))}
                </ul>
              </div>
            )}
          </div>
        )}
        {error && <p className="interview-chat-error">{error}</p>}
      </section>
    </div>
  );
}
