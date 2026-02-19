import { useParams } from "react-router-dom";
import { useProblemsQuery } from "../hooks/useProblemsQuery";
import ProblemGrid from "../components/ProblemGrid";

export default function ProblemListPage() {
  const { id } = useParams();
  const { data, isLoading, isError, error } = useProblemsQuery(id ?? "");

  return (
    <section className="simple-page">
      <h1>{data?.name ?? "Problem List"}</h1>
      {isLoading && <p className="status-line">Loading problem lists...</p>}
      {isError && (
        <p className="status-line error">
          {(error as Error).message || "Request failed."}
        </p>
      )}
      {!isLoading && !isError && data && data.problems.length > 0 && (
        <ProblemGrid problems={data.problems} />
      )}
      {!isLoading && !isError && data?.problems.length === 0 && (
        <p className="status-line">No problem lists found yet.</p>
      )}
    </section>
  );
}
