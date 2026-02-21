import { useEffect, useMemo, useState } from "react";
import { useParams } from "react-router-dom";
import { useProblemQuery } from "../../hooks/useProblemQuery";
import "./ProblemPage.css";

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

export default function ProblemPage() {
  const { id } = useParams();
  const { data, isLoading, isError, error } = useProblemQuery(id ?? "");
  const [selectedLanguage, setSelectedLanguage] = useState("javascript");
  const [code, setCode] = useState("");
  const [terminalLines, setTerminalLines] = useState<string[]>(TERMINAL_HINTS);

  const starterCode = data?.starter_code ?? FALLBACK_STARTER_CODE;
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

  const runCode = () => {
    setTerminalLines((prev) => [
      ...prev,
      `$ Running ${data?.title ?? "problem"}...`,
      "$ Done. (Runner integration pending)",
    ]);
  };

  const submitCode = () => {
    setTerminalLines((prev) => [
      ...prev,
      "$ Submitting solution...",
      "$ Submission endpoint not connected yet.",
    ]);
  };

  return (
    <section className="problem-workspace" aria-label="Coding workspace">
      {isLoading && <p className="status-line">Loading problem...</p>}
      {isError && (
        <p className="status-line error">
          {(error as Error).message || "Request failed."}
        </p>
      )}

      {!isLoading && !isError && data && (
        <div className="problem-layout">
          <article className="problem-panel" aria-labelledby="problem-title">
            <header className="problem-panel-header">
              <h1 id="problem-title">{data.title}</h1>
              <p className="problem-meta">
                <span>{data.category}</span>
                <span aria-hidden="true"> • </span>
                <span>{data.difficulty}</span>
              </p>
            </header>

            <section className="problem-description">
              <h2>Description</h2>
              <p>{data.description}</p>
            </section>
          </article>

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
                onChange={(event) => setCode(event.target.value)}
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
        </div>
      )}
    </section>
  );
}
