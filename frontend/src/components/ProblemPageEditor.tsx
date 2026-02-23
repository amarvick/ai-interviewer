import { useEffect, useMemo, useState } from "react";
import type { Problem } from "../types/problem";
import "./ProblemPageEditor.css";
import ProblemPageCodeEditor from "./ProblemPageCodeEditor";
import ProblemPageTerminal from "./ProblemPageTerminal";

interface ProblemPageEditorProps {
  problem: Problem;
}

const FALLBACK_STARTER_CODE: Record<string, string> = {
  python: "class Solution:\n    def solve(self):\n        pass\n",
  javascript: "class Solution {\n  solve() {\n    \n  }\n}\n",
  java: "class Solution {\n    public void solve() {\n        \n    }\n}\n",
  cpp: "class Solution {\npublic:\n    void solve() {\n        \n    }\n};\n",
};

const TERMINAL_HINTS = [
  "$ Ready.",
  "$ Click Run to execute against sample input.",
  "$ Click Submit to send your final solution.",
];

function normalizeStarterCode(input: unknown): Record<string, string> {
  if (!input || typeof input !== "object") {
    return {};
  }

  const normalized: Record<string, string> = {};
  for (const [key, value] of Object.entries(input)) {
    if (typeof value === "string") {
      normalized[key] = value;
    }
  }
  return normalized;
}

export default function ProblemPageEditor({ problem }: ProblemPageEditorProps) {
  const [selectedLanguage, setSelectedLanguage] = useState("javascript");
  const [codeByLanguage, setCodeByLanguage] = useState<Record<string, string>>(
    FALLBACK_STARTER_CODE
  );
  const [terminalLines, setTerminalLines] = useState<string[]>(TERMINAL_HINTS);

  const starterCode = normalizeStarterCode(problem?.starter_code);
  const languageOptions = useMemo(
    () => ["python", "javascript", "java", "cpp"],
    []
  );

  useEffect(() => {
    const mergedCode: Record<string, string> = {
      ...FALLBACK_STARTER_CODE,
      ...starterCode,
    };
    setCodeByLanguage(mergedCode);

    const initialLanguage = mergedCode.javascript
      ? "javascript"
      : languageOptions[0];
    setSelectedLanguage(initialLanguage);
  }, [languageOptions, starterCode]);

  const handleEditorChange = (value: string | undefined) => {
    setCodeByLanguage((prev) => ({
      ...prev,
      [selectedLanguage]: value ?? "",
    }));
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

  const activeCode = codeByLanguage[selectedLanguage] ?? "";

  return (
    <div className="editor-stack">
      <ProblemPageCodeEditor
        selectedLanguage={selectedLanguage}
        languageOptions={languageOptions}
        code={activeCode}
        onLanguageChange={setSelectedLanguage}
        onCodeChange={handleEditorChange}
        onRun={runCode}
        onSubmit={submitCode}
      />
      <ProblemPageTerminal lines={terminalLines} />
    </div>
  );
}
