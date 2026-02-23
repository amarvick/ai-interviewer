import { useMemo, useState } from "react";
import type { Problem } from "../types/problem";
import "./ProblemPageEditor.css";
import ProblemPageTerminal from "./ProblemPageTerminal";
import ProblemPageCodeEditor from "./ProblemPageCodeEditor";
import ProblemPageEditorToolbar from "./ProblemPageEditorToolbar";

interface ProblemPageEditorProps {
  problem: Problem;
}

const FALLBACK_STARTER_CODE: Record<string, string> = {
  javascript: `class Solution {\n  twoSum = function(nums, target) {\n      \n  };\n}\n`,
};

const TERMINAL_HINTS = [
  "$ Ready.",
  "$ Click Run to execute against sample input.",
  "$ Click Submit to send your final solution.",
];

export default function ProblemPageEditor({ problem }: ProblemPageEditorProps) {
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
    </div>
  );
}
