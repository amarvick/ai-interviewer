import { useEffect, useMemo, useState, type KeyboardEvent } from "react";
import type { Problem } from "../types/problem";
import "./ProblemPageEditor.css";

interface ProblemPageEditorProps {
  problem: Problem;
}

const FALLBACK_STARTER_CODE: Record<string, string> = {
  javascript: `class Solution {\n  twoSum = function(nums, target) {\n      \n  };\n}\n`,
};

const LANGUAGE_LABELS: Record<string, string> = {
  python: "Python",
  javascript: "JavaScript",
  java: "Java",
  cpp: "C++",
};

const TERMINAL_HINTS = [
  "$ Ready.",
  "$ Click Run to execute against sample input.",
  "$ Click Submit to send your final solution.",
];

export default function ProblemPageEditor({ problem }: ProblemPageEditorProps) {
  const [selectedLanguage, setSelectedLanguage] = useState("javascript");
  const [code, setCode] = useState("");
  const [terminalLines, setTerminalLines] = useState<string[]>(TERMINAL_HINTS);

  const starterCode = problem?.starter_code ?? FALLBACK_STARTER_CODE;
  const languageOptions = useMemo(() => {
    const keys = Object.keys(starterCode);
    return keys.length > 0 ? keys : ["javascript"];
  }, [starterCode]);

  useEffect(() => {
    const initialLanguage = languageOptions[0]; // Default OR go to user settings and get preferred language
    // TODO later - allow button to set default language IF the user wants
    setSelectedLanguage(initialLanguage);
    setCode(starterCode[initialLanguage] ?? "");
  }, [languageOptions, starterCode]);

  const handleLanguageChange = (nextLanguage: string) => {
    setSelectedLanguage(nextLanguage);
    setCode(starterCode[nextLanguage] ?? "");
    setTerminalLines((prev) => [
      ...prev,
      `$ Switched language to ${nextLanguage}.`,
    ]);
  };

  const updateCode = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    setCode(e.currentTarget.value);
  };

  const onKeyDown = (e: KeyboardEvent<HTMLTextAreaElement>) => {
    if (e.key === "Tab") {
      e.preventDefault();
      document.execCommand("insertText", false, "\t");
    }
  };

  const runCode = () => {
    setTerminalLines((prev) => [
      ...prev,
      `$ Running ${problem?.title ?? "problem"}...`,
      "$ Done. (Runner integration pending)",
    ]);
    // TODO -- integrate with runner service to execute code and display results
  };

  const submitCode = () => {
    setTerminalLines((prev) => [
      ...prev,
      "$ Submitting solution...",
      "$ Submission endpoint not connected yet.",
    ]);
    // TODO -- integrate with submission endpoint to send code and receive feedback on test cases
  };
  return (
    <div className="editor-stack">
      <section className="editor-panel" aria-label="Code editor">
        <div className="editor-toolbar">
          <label htmlFor="editor-language">Language</label>
          <select
            id="editor-language"
            value={selectedLanguage}
            onChange={(event) => handleLanguageChange(event.target.value)}
          >
            {languageOptions.map((language) => (
              <option key={language} value={language}>
                {LANGUAGE_LABELS[language] ?? language}
              </option>
            ))}
          </select>

          <div className="toolbar-actions">
            <button type="button" onClick={runCode}>
              Run
            </button>
            <button type="button" onClick={submitCode}>
              Submit
            </button>
          </div>
        </div>

        <label htmlFor="code-editor" className="sr-only">
          Code editor
        </label>
        <textarea
          id="code-editor"
          className="code-editor"
          value={code}
          onKeyDown={(event) => onKeyDown(event)}
          onChange={(event) => updateCode(event)}
          spellCheck={false}
        />
      </section>

      <section className="terminal-panel" aria-label="Terminal output">
        <header className="terminal-header">Terminal</header>
        <pre className="terminal-output">
          {terminalLines.map((line, index) => (
            <span key={`${line}-${index}`}>{line}</span>
          ))}
        </pre>
      </section>
    </div>
  );
}
