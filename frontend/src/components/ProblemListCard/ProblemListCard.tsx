import { Link } from "react-router-dom";
import type { ProblemList } from "../../types/problem";
import "./ProblemListCard.css";

interface ProblemListCardProps {
  problemList: ProblemList;
}

export default function ProblemListCard({ problemList }: ProblemListCardProps) {
  return (
    <Link to={`/list/${problemList.id}`} className="problem-list-card">
      <div className="problem-card-icon-wrap">
        <img
          src={problemList.icon_url}
          alt={`${problemList.name} icon`}
          className="problem-card-icon"
          loading="lazy"
        />
      </div>
      <h3 className="problem-list-card-title">{problemList.name}</h3>
    </Link>
  );
}
