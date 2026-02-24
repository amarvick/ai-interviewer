interface ProblemPageEditorToolbarProps {
  selectedLanguage: string;
  handleLanguageChange: (nextLanguage: string) => void;
  languageOptions: string[];
  setTerminalLines: React.Dispatch<React.SetStateAction<string[]>>;
  problemTitle?: string;
}

const LANGUAGE_LABELS: Record<string, string> = {
  python: "Python",
  javascript: "JavaScript",
  java: "Java",
  cpp: "C++",
};

export default function ProblemPageEditorToolbar({
  selectedLanguage,
  handleLanguageChange,
  languageOptions,
  setTerminalLines,
  problemTitle,
}: ProblemPageEditorToolbarProps) {
  const runCode = () => {
    setTerminalLines((prev) => [
      ...prev,
      `$ Running ${problemTitle ?? "problem"}...`,
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
  );
}
