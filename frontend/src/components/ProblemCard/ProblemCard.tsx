import { Link } from "react-router-dom";
import type { Problem } from "../../types/problem";
import "./ProblemCard.css";

interface ProblemCardProps {
  problem: Problem;
}

export default function ProblemCard({ problem }: ProblemCardProps) {
  const category = problem.category.trim();
  const difficulty = String(problem.difficulty).trim();
  const isPassed = Boolean(problem.is_passed);

  return (
    <article
      className="problem-card"
      aria-label={`${problem.title}. ${category} problem. ${difficulty} difficulty.`}
    >
      <div className="problem-card-left">
        <span
          className={
            isPassed
              ? "problem-status-indicator passed"
              : "problem-status-indicator"
          }
          aria-label={isPassed ? "Solved problem" : "Unsolved problem"}
        >
          {isPassed ? "✓" : ""}
        </span>

        <div className="problem-card-details">
          <h3 className="problem-card-title">{problem.title}</h3>
          <p
            className="problem-card-meta"
            aria-label={`Problem type ${category}, difficulty ${difficulty}`}
          >
            {category} • {difficulty}
          </p>
        </div>
      </div>

      <div className="problem-card-actions">
        <Link to={`/problem/${problem.id}`} className="problem-card-action primary">
          Problem
        </Link>
        <Link
          to={`/interview-problem/${problem.id}`}
          className="problem-card-action secondary"
        >
          Interview
        </Link>
      </div>
    </article>
  );
}
