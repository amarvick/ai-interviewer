import type { ReactNode } from "react";
import { useProblemQuery } from "../../hooks/useProblemQuery";
import type { Problem } from "../../types/problem";
import ProblemPageDescription from "../ProblemPageDescription/ProblemPageDescription";
import SplitPane from "../SplitPane/SplitPane";
import "./ProblemWorkspace.css";

interface ProblemWorkspaceProps {
  problemId: string;
  secondary: (problem: Problem) => ReactNode;
  workspaceClassName?: string;
}

export default function ProblemWorkspace({
  problemId,
  secondary,
  workspaceClassName = "problem-workspace",
}: ProblemWorkspaceProps) {
  const { data, isLoading, isError, error } = useProblemQuery(problemId);

  return (
    <section className={workspaceClassName} aria-label="Coding workspace">
      {isLoading && <p className="status-line">Loading problem...</p>}
      {isError && (
        <p className="status-line error">
          {(error as Error).message || "Request failed."}
        </p>
      )}
      {!isLoading && !isError && data && (
        <SplitPane
          orientation="vertical"
          defaultPrimarySize={42}
          minPrimarySize={28}
          maxPrimarySize={72}
          className="problem-layout"
          primary={<ProblemPageDescription problem={data} />}
          secondary={secondary(data)}
        />
      )}
    </section>
  );
}
