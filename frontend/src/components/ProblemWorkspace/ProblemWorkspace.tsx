import type { ReactNode } from "react";
import { useProblemQuery } from "../../hooks/useProblemQuery";
import type { Problem } from "../../types/problem";
import ProblemPageDescription from "../ProblemPageDescription/ProblemPageDescription";
import SplitPane from "../SplitPane/SplitPane";
import "./ProblemWorkspace.css";

interface ProblemWorkspaceProps {
  problemId: string;
  secondaryComponent: (problem: Problem) => ReactNode;
  workspaceClassName?: string;
  splitDefaultPrimarySize?: number;
  splitMinPrimarySize?: number;
  splitMaxPrimarySize?: number;
}

export default function ProblemWorkspace({
  problemId,
  secondaryComponent,
  workspaceClassName = "problem-workspace",
  splitDefaultPrimarySize = 42,
  splitMinPrimarySize = 28,
  splitMaxPrimarySize = 72,
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
          defaultPrimarySize={splitDefaultPrimarySize}
          minPrimarySize={splitMinPrimarySize}
          maxPrimarySize={splitMaxPrimarySize}
          className="problem-layout"
          primary={<ProblemPageDescription problem={data} />}
          secondary={secondaryComponent(data)}
        />
      )}
    </section>
  );
}
