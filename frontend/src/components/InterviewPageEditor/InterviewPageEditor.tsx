import { useEffect, useRef } from "react";
import type { Problem } from "../../types/problem";
import ProblemPageCodeEditor from "../ProblemPageCodeEditor/ProblemPageCodeEditor";
import ProblemPageEditorToolbar from "../ProblemPageEditorToolbar/ProblemPageEditorToolbar";
import SplitPane from "../SplitPane/SplitPane";
import { useInterviewSession } from "../../hooks/useInterviewSession";
import "./InterviewPageEditor.css";

interface InterviewPageEditorProps {
  problem: Problem;
}

export default function InterviewPageEditor({
  problem,
}: InterviewPageEditorProps) {
  const chatMessagesRef = useRef<HTMLDivElement | null>(null);
  const inputRef = useRef<HTMLTextAreaElement | null>(null);

  const {
    languageOptions,
    selectedLanguage,
    code,
    draftMessage,
    messages,
    sessionStatus,
    canSubmit,
    activeTab,
    completionResult,
    isSending,
    isSubmittingCode,
    isLoadingFeedback,
    error,
    rubricRows,
    nitpicks,
    finalScore,
    didPass,
    hasSession,
    setDraftMessage,
    setActiveTab,
    handleLanguageChange,
    updateCode,
    handleSend,
    handleSubmitCode,
    handleDraftKeyDown,
  } = useInterviewSession(problem);

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
                      !hasSession ||
                      !draftMessage.trim()
                    }
                  >
                    {isSending ? "Sending..." : "Send"}
                  </button>
                </footer>
              </>
            ) : (
              <div className="interview-feedback-panel">
                {isLoadingFeedback ? (
                  <div className="feedback-loading" role="status" aria-live="polite">
                    <span className="feedback-spinner" aria-hidden="true" />
                    <span>Generating feedback...</span>
                  </div>
                ) : (
                  <>
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
                  </>
                )}
              </div>
            )}
            {error && <p className="interview-chat-error">{error}</p>}
          </section>
        }
      />
    </div>
  );
}
