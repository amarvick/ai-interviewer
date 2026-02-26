import { Link } from "react-router-dom";
import type { Problem } from "../types/problem";
import "./ProblemCard.css";

interface ProblemCardProps {
  problem: Problem;
}

export default function ProblemCard({ problem }: ProblemCardProps) {
  const category = problem.category.trim();
  const difficulty = String(problem.difficulty).trim();
  const isPassed = Boolean(problem.is_passed);

  return (
    <Link
      to={`/problem/${problem.id}`}
      className="problem-card"
      aria-label={`${problem.title}. ${category} problem. ${difficulty} difficulty.`}
    >
      <span
        className={isPassed ? "problem-status-indicator passed" : "problem-status-indicator"}
        aria-label={isPassed ? "Solved problem" : "Unsolved problem"}
      >
        {isPassed ? "✓" : ""}
      </span>
      <span className="problem-card-title">{problem.title}</span>
      <span
        className="problem-card-meta"
        aria-label={`Problem type ${category}, difficulty ${difficulty}`}
      >
        {category} • {difficulty}
      </span>
    </Link>
  );
}
