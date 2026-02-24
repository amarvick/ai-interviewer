<<<<<<< HEAD
import { useEffect, useMemo, useState } from "react";
import type { Problem } from "../types/problem";
import "./ProblemPageEditor.css";
import ProblemPageCodeEditor from "./ProblemPageCodeEditor";
import ProblemPageTerminal from "./ProblemPageTerminal";
=======
import { useMemo, useState } from "react";
import type { Problem } from "../types/problem";
import "./ProblemPageEditor.css";
import ProblemPageTerminal from "./ProblemPageTerminal";
import ProblemPageCodeEditor from "./ProblemPageCodeEditor";
import ProblemPageEditorToolbar from "./ProblemPageEditorToolbar";
>>>>>>> recovery-branch-new-css

// TODO - Rework this file later. For now, just want to get something functional in place.
interface ProblemPageEditorProps {
  problem: Problem;
}

const FALLBACK_STARTER_CODE: Record<string, string> = {
<<<<<<< HEAD
  python: "class Solution:\n    def solve(self):\n        pass\n",
  javascript: "class Solution {\n  solve() {\n    \n  }\n}\n",
  java: "class Solution {\n    public void solve() {\n        \n    }\n}\n",
  cpp: "class Solution {\npublic:\n    void solve() {\n        \n    }\n};\n",
=======
  javascript: `class Solution {\n  twoSum = function(nums, target) {\n      \n  };\n}\n`,
>>>>>>> recovery-branch-new-css
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
<<<<<<< HEAD
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
=======
  const starterCode = problem?.starter_code ?? FALLBACK_STARTER_CODE;
  const languageOptions = useMemo(() => {
    const keys = Object.keys(starterCode);
    return keys.length > 0 ? keys : ["javascript"];
  }, [starterCode]);

  const [selectedLanguage, setSelectedLanguage] = useState(
    languageOptions[0] ?? "javascript"
  );
  const [code, setCode] = useState(starterCode[selectedLanguage] ?? "");
  const [terminalLines, setTerminalLines] = useState<string[]>(TERMINAL_HINTS);
>>>>>>> recovery-branch-new-css

  const handleEditorChange = (value: string | undefined) => {
    setCodeByLanguage((prev) => ({
      ...prev,
<<<<<<< HEAD
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
=======
      `$ Switched language to ${nextLanguage}.`,
    ]);
  };

  const updateCode = (value: string | undefined) => {
    setCode(value ?? "");
  };

  return (
    <div className="editor-stack">
      <section className="editor-panel" aria-label="Code editor">
        <ProblemPageEditorToolbar
          selectedLanguage={selectedLanguage}
          handleLanguageChange={handleLanguageChange}
          languageOptions={languageOptions}
          setTerminalLines={setTerminalLines}
          problemTitle={problem?.title}
        />

        <ProblemPageCodeEditor
          selectedLanguage={selectedLanguage}
          updateCode={updateCode}
          code={code}
        />
      </section>

      <ProblemPageTerminal lines={terminalLines} aria-label="Terminal output" />
>>>>>>> recovery-branch-new-css
    </div>
  );
}
