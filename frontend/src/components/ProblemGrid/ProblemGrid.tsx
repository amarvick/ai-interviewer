import type { Problem } from "../../types/problem";
import ProblemCard from "../ProblemCard/ProblemCard";
import "./ProblemGrid.css";

interface ProblemGridProps {
  problems: Problem[];
}

export default function ProblemGrid({ problems }: ProblemGridProps) {
  return (
    <section className="problem-grid">
      {/* TODO - Include sorting component here */}
      {problems.map((problem) => (
        <ProblemCard key={problem.id} problem={problem} />
      ))}
    </section>
  );
}
