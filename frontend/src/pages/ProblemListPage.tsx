import { useParams } from "react-router-dom";
import { useProblemsQuery } from "../hooks/useProblemsQuery";
import ProblemGrid from "../components/ProblemGrid";

export default function ProblemListPage() {
  const { id } = useParams();
  const { data: problems, isLoading, isError, error } = useProblemsQuery(id!);

  console.log("****** PROBLEMS", problems);

  return (
    <section className="simple-page">
      <h1>Problem List</h1>{" "}
      {isLoading && <p className="status-line">Loading problem lists...</p>}
      {isError && (
        <p className="status-line error">
          {(error as Error).message || "Request failed."}
        </p>
      )}
      {!isLoading && !isError && problems && problems.length > 0 && (
        <ProblemGrid problems={problems} />
      )}
      {!isLoading && !isError && problems?.length === 0 && (
        <p className="status-line">No problem lists found yet.</p>
      )}
    </section>
  );
}
