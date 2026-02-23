import "./ProblemPageTerminal.css";

interface ProblemPageTerminalProps {
  lines: string[];
}

// TODO - Don't make this a terminal, make it show 3 test cases on
// One tab and then show terminal output on another tab. For now, just want to get something functional in place.
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
