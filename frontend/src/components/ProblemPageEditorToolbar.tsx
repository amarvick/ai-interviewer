interface ProblemPageEditorToolbarProps {
  selectedLanguage: string;
  handleLanguageChange: (nextLanguage: string) => void;
  languageOptions: string[];
  onSubmit: () => void;
  isSubmitting: boolean;
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
  onSubmit,
  isSubmitting,
}: ProblemPageEditorToolbarProps) {
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
        <button type="button" onClick={onSubmit} disabled={isSubmitting}>
          {isSubmitting ? "Submitting..." : "Submit"}
        </button>
      </div>
    </div>
  );
}
