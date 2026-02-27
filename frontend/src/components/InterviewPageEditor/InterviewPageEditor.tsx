import { useMemo, useState } from "react";
import type { Problem } from "../../types/problem";
import ProblemPageCodeEditor from "../ProblemPageCodeEditor/ProblemPageCodeEditor";
import ProblemPageEditorToolbar from "../ProblemPageEditorToolbar/ProblemPageEditorToolbar";
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
  const [messages, setMessages] = useState<ChatMessage[]>([
    {
      id: "ai-intro",
      role: "ai",
      content:
        "Hi, I am your interviewer. Start by explaining your approach, then ask me clarifying questions.",
    },
  ]);

  const handleLanguageChange = (nextLanguage: string) => {
    setSelectedLanguage(nextLanguage);
    setCode(starterCode[nextLanguage] ?? "");
  };

  const updateCode = (value: string | undefined) => {
    setCode(value ?? "");
  };

  const handleSend = () => {
    const content = draftMessage.trim();
    if (!content) {
      return;
    }

    const userMessage: ChatMessage = {
      id: `you-${Date.now()}`,
      role: "you",
      content,
    };

    const aiReply: ChatMessage = {
      id: `ai-${Date.now() + 1}`,
      role: "ai",
      content:
        "Good direction. Talk through time/space complexity next, and explain tradeoffs with one alternative approach.",
    };

    setMessages((prev) => [...prev, userMessage, aiReply]);
    setDraftMessage("");
  };

  return (
    <div className="interview-editor-stack">
      <section className="editor-panel" aria-label="Code editor">
        <ProblemPageEditorToolbar
          selectedLanguage={selectedLanguage}
          handleLanguageChange={handleLanguageChange}
          languageOptions={languageOptions}
          onSubmit={handleSend}
          isSubmitting={false}
          submitLabel="Ask AI"
          submittingLabel="Thinking..."
        />
        <ProblemPageCodeEditor
          selectedLanguage={selectedLanguage}
          updateCode={updateCode}
          code={code}
        />
      </section>

      <section className="interview-chat-panel" aria-label="AI interview panel">
        <header className="interview-chat-header">AI Interview Panel</header>
        <div className="interview-chat-messages">
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
          <button type="button" onClick={handleSend}>
            Send
          </button>
        </footer>
      </section>
    </div>
  );
}
