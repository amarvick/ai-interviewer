import type { Problem } from "../types/problem";
import "./ProblemPageDescription.css";

interface ProblemPageDescriptionProps {
  problem: Problem;
}

export default function ProblemPageDescription({
  problem,
}: ProblemPageDescriptionProps) {
  return (
    <article className="problem-panel" aria-labelledby="problem-title">
      <header className="problem-panel-header">
        <h1 id="problem-title">{problem.title}</h1>
        <p className="problem-meta">
          <span>{problem.category}</span>
          <span aria-hidden="true"> • </span>
          <span>{problem.difficulty}</span>
        </p>
      </header>

      <section className="problem-description">
        <h2>Description</h2>
        <p>{problem.description}</p>
      </section>
    </article>
  );
}
