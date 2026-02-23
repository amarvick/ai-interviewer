import { useEffect, useMemo, useState } from "react";
import Editor, { type BeforeMount } from "@monaco-editor/react";
import type { Problem } from "../types/problem";
import "./ProblemPageEditor.css";
import ProblemPageTerminal from "./ProblemPageTerminal";

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

const defineTheme: BeforeMount = (monaco) => {
  monaco.editor.defineTheme("ai-interviewer-violet", {
    base: "vs-dark",
    inherit: true,
    rules: [
      { token: "", foreground: "EAF0FF", background: "0B1022" },
      { token: "comment", foreground: "8DA0D3" },
      { token: "keyword", foreground: "C5A3FF" },
      { token: "string", foreground: "9EE6B8" },
      { token: "number", foreground: "7EC8FF" },
      { token: "type.identifier", foreground: "8FB5FF" },
    ],
    colors: {
      "editor.background": "#0B1022",
      "editor.foreground": "#EAF0FF",
      "editorLineNumber.foreground": "#5A6691",
      "editorLineNumber.activeForeground": "#C8D6FF",
      "editorCursor.foreground": "#B48CFF",
      "editor.selectionBackground": "#35245D",
      "editor.inactiveSelectionBackground": "#2A2440",
      "editor.lineHighlightBackground": "#131B35",
      "editorIndentGuide.background1": "#252F52",
    },
  });
};

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

  const updateCode = (value: string | undefined) => {
    setCode(value ?? "");
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

        <div className="editor-monaco-wrap">
          <Editor
            height="100%"
            language={selectedLanguage}
            theme="ai-interviewer-violet"
            value={code}
            beforeMount={defineTheme}
            onChange={updateCode}
            options={{
              fontSize: 14,
              autoClosingBrackets: "languageDefined",
              minimap: { enabled: false },
              tabSize: 4,
              insertSpaces: true,
              smoothScrolling: true,
              padding: { top: 10 },
            }}
          />
        </div>
      </section>

      <ProblemPageTerminal lines={terminalLines} aria-label="Terminal output" />
    </div>
  );
}
