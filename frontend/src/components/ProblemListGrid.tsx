import ProblemListCard from "./ProblemListCard";
import type { ProblemList } from "../types/problem";
import "./ProblemListGrid.css";

interface ProblemListGridProps {
  problemLists: ProblemList[];
}

export default function ProblemListGrid({
  problemLists,
}: ProblemListGridProps) {
  return (
    <section className="problem-list-grid">
      {problemLists.map((list) => (
        <ProblemListCard key={list.id} problemList={list} />
      ))}
    </section>
  );
}
