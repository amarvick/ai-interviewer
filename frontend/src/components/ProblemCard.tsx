import { Link } from "react-router-dom";
import type { Problem } from "../types/problem";

interface ProblemCardProps {
  problem: Problem;
}

export default function ProblemCard({ problem }: ProblemCardProps) {
  return (
    <Link to={`/problem/${problem.id}`} className="problem-card">
      <div className="problem-card-icon-wrap">
        <img
          alt={`${problem.title} icon`}
          className="problem-card-i con"
          loading="lazy"
        />
      </div>
      <h3 className="problem-card-title">{problem.title}</h3>
    </Link>
  );
}
