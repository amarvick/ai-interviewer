import "./ProblemPageTerminal.css";

interface ProblemPageTerminalProps {
  lines: string[];
}

export default function ProblemPageTerminal({
  lines,
}: ProblemPageTerminalProps) {
  return (
    <section className="terminal-panel" aria-label="Terminal output">
      <header className="terminal-header">Terminal</header>
      <pre className="terminal-output">
        {lines.map((line, index) => (
          <span key={`${line}-${index}`}>{line}</span>
        ))}
      </pre>
    </section>
  );
}
