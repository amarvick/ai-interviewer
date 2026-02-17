import { useEffect, useState } from "react";
import { Link, NavLink, useNavigate } from "react-router-dom";
import { clearAuthToken, isAuthenticated, onAuthChanged } from "../services/auth";

export default function Navbar() {
  const [loggedIn, setLoggedIn] = useState<boolean>(isAuthenticated());
  const navigate = useNavigate();

  useEffect(() => {
    return onAuthChanged(() => {
      setLoggedIn(isAuthenticated());
    });
  }, []);

  const handleLogout = () => {
    clearAuthToken();
    navigate("/");
  };

  return (
    <header className="navbar-shell">
      <nav className="navbar">
        <Link to="/" className="brand">
          AI Interviewer
        </Link>

        <div className="nav-links">
          <NavLink
            to="/"
            className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
            end
          >
            Home
          </NavLink>

          {loggedIn ? (
            <button type="button" className="nav-link button-link" onClick={handleLogout}>
              Logout
            </button>
          ) : (
            <NavLink
              to="/login"
              className={({ isActive }) => (isActive ? "nav-link active" : "nav-link")}
            >
              Login / Signup
            </NavLink>
          )}
        </div>
      </nav>
    </header>
  );
}
