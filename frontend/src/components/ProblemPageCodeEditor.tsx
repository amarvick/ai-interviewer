import Editor, { type BeforeMount } from "@monaco-editor/react";

interface ProblemPageCodeEditorProps {
  selectedLanguage: string;
  updateCode: (value: string | undefined) => void;
  code: string;
}

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

export default function ProblemPageCodeEditor({
  selectedLanguage,
  updateCode,
  code,
}: ProblemPageCodeEditorProps) {
  return (
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
  );
}
