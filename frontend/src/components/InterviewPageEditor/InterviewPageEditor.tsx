import { useEffect, useMemo, useState } from "react";
import type { Problem } from "../../types/problem";
import ProblemPageCodeEditor from "../ProblemPageCodeEditor/ProblemPageCodeEditor";
import ProblemPageEditorToolbar from "../ProblemPageEditorToolbar/ProblemPageEditorToolbar";
import {
  getInterviewSession,
  postInterviewMessage,
  runSubmission,
  startInterviewSession,
} from "../../services/api";
import type { InterviewSessionDetailResponse } from "../../types/interview";
import "./InterviewPageEditor.css";

interface InterviewPageEditorProps {
  problem: Problem;
}

interface ChatMessage {
  id: string;
  role: "ai" | "you";
  content: string;
}

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
  const [isSending, setIsSending] = useState(false);
  const [isSubmittingCode, setIsSubmittingCode] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initializeSession = async () => {
      setError(null);
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

    setDraftMessage("");
    setIsSending(true);
    setError(null);
    try {
      const detail = await postInterviewMessage(sessionId, {
        content,
        role: "user",
        has_submission: false,
      });
      applySession(detail);
    } catch (sendError) {
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

  const applySession = (detail: InterviewSessionDetailResponse) => {
    setSessionId(detail.id);
    setSessionStage(detail.stage);
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
          <span className="stage-pill">{sessionStage}</span>
        </header>
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
        {error && <p className="interview-chat-error">{error}</p>}
      </section>
    </div>
  );
}
