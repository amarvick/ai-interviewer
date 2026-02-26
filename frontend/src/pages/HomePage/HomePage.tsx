import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import ProblemListGrid from "../../components/ProblemListGrid";
import { useProblemListsQuery } from "../../hooks/useProblemListsQuery";
import { isAuthenticated, onAuthChanged } from "../../services/auth";
import "./HomePage.css";

export default function HomePage() {
  const [loggedIn, setLoggedIn] = useState<boolean>(isAuthenticated());
  const {
    data: problemLists,
    isLoading,
    isError,
    error,
  } = useProblemListsQuery(loggedIn);

  useEffect(() => {
    return onAuthChanged(() => {
      setLoggedIn(isAuthenticated());
    });
  }, []);

  if (!loggedIn) {
    return (
      <div className="home-page home-page-landing">
        <section className="hero">
          <h1 className="hero-title">AI Interviewer</h1>
          <p className="hero-copy">
            Practice real coding interview problems, track your progress, and
            sharpen your communication under pressure.
          </p>
          <div className="hero-actions">
            <Link to="/login" className="hero-cta">
              Login
            </Link>
            <Link to="/signup" className="hero-cta secondary">
              Create Account
            </Link>
          </div>
        </section>
      </div>
    );
  }

  return (
    <div className="home-page">
      <section className="lists-section">
        <div className="section-header">
          <h2>Practice Sets</h2>
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
