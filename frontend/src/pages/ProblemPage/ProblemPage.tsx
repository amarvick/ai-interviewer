import { useParams } from "react-router-dom";
import { useProblemQuery } from "../../hooks/useProblemQuery";
import "./ProblemPage.css";
import ProblemPageDescription from "../../components/ProblemPageDescription";
import ProblemPageEditor from "../../components/ProblemPageEditor";
import SplitPane from "../../components/SplitPane";

export default function ProblemPage() {
  const { id } = useParams();
  const { data, isLoading, isError, error } = useProblemQuery(id ?? "");

  return (
    <section className="problem-workspace" aria-label="Coding workspace">
      {/* TODO - consider skeleton outline instead */}
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
          secondary={<ProblemPageEditor problem={data} />}
        />
      )}
    </section>
  );
}
