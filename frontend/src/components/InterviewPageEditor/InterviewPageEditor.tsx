import { useEffect, useMemo, useRef, useState } from "react";
import type { KeyboardEvent } from "react";
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
  createdAt: number;
}

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
  const [isEditorUnlocked, setIsEditorUnlocked] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [isSubmittingCode, setIsSubmittingCode] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const initializeSession = async () => {
      setError(null);
      setIsEditorUnlocked(false);
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
        sendError instanceof Error
          ? sendError.message
          : "Failed to send message.";
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

      const nextMessages = sortMessagesByTime([
        ...messages,
        {
          id: `submission-${Date.now()}`,
          role: "you",
          content: submissionSummary,
          createdAt: Date.now(),
        },
      ]);
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
    setIsEditorUnlocked((prev) => prev || Boolean(detail.can_code));
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

  return (
    <div className="interview-editor-stack">
      <section
        className={`editor-panel ${
          isEditorUnlocked ? "editor-panel-active" : "editor-panel-locked"
        }`}
        aria-label="Code editor"
      >
        <ProblemPageEditorToolbar
          selectedLanguage={selectedLanguage}
          handleLanguageChange={handleLanguageChange}
          languageOptions={languageOptions}
          onSubmit={handleSubmitCode}
          isSubmitting={isSubmittingCode}
          isSubmitDisabled={!isEditorUnlocked}
          submitLabel="Submit Code"
          submittingLabel="Submitting..."
        />
        <ProblemPageCodeEditor
          selectedLanguage={selectedLanguage}
          updateCode={updateCode}
          code={code}
          readOnly={!isEditorUnlocked}
          className={
            isEditorUnlocked ? "editor-shell-active" : "editor-shell-locked"
          }
        />
      </section>

      <section className="interview-chat-panel" aria-label="AI interview panel">
        <header className="interview-chat-header">
          <span>AI Interview Panel</span>
        </header>
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
        {error && <p className="interview-chat-error">{error}</p>}
      </section>
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
