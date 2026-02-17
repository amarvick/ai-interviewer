import { Link } from "react-router-dom";
import ProblemListGrid from "../components/ProblemListGrid";
import { useProblemListsQuery } from "../hooks/useProblemListsQuery";

export default function HomePage() {
  const {
    data: problemLists,
    isLoading,
    isError,
    error,
  } = useProblemListsQuery();
  console.log("Fetched problem lists:", problemLists);

  return (
    <div className="home-page">
      <section className="hero">
        <h1 className="hero-title">AI Interviewer</h1>
        <p className="hero-copy">
          Drill realistic coding sets, practice with time pressure, and get
          feedback fast.
        </p>
        <Link to="/login" className="hero-cta">
          Start Practicing
        </Link>
      </section>

      <section className="lists-section">
        <div className="section-header">
          <h2>Problem Lists</h2>
          <span>{problemLists?.length ?? 0} available</span>
        </div>

        {isLoading && <p className="status-line">Loading problem lists...</p>}
        {isError && (
          <p className="status-line error">
            {(error as Error).message || "Request failed."}
          </p>
        )}
        {!isLoading && !isError && problemLists && problemLists.length > 0 && (
          <ProblemListGrid problemLists={problemLists} />
        )}
        {!isLoading && !isError && problemLists?.length === 0 && (
          <p className="status-line">No problem lists found yet.</p>
        )}
      </section>
    </div>
  );
}
