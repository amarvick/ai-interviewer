import { useEffect, useState } from "react";
import type { FormEvent } from "react";
import { Link, useNavigate } from "react-router-dom";
import { login } from "../../services/api";
import { isAuthenticated, onAuthChanged, setAuthToken } from "../../services/auth";
import "./LoginPage.css";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const navigate = useNavigate();

  useEffect(() => {
    const redirectIfAuthenticated = () => {
      if (isAuthenticated()) {
        navigate("/", { replace: true });
      }
    };

    redirectIfAuthenticated();
    return onAuthChanged(redirectIfAuthenticated);
  }, [navigate]);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    setLoading(true);

    try {
      const result = await login({ email, password });
      setAuthToken(result.access_token);
      navigate("/");
    } catch (submitError) {
      const message =
        submitError instanceof Error
          ? submitError.message
          : "Login failed. Please retry.";
      setError(message);
    } finally {
      setLoading(false);
    }
  };

  return (
    <section className="auth-page">
      <h1>Login</h1>
      <form className="auth-form" onSubmit={handleSubmit}>
        <label>
          Email
          <input
            type="email"
            value={email}
            onChange={(event) => setEmail(event.target.value)}
            required
            autoComplete="email"
          />
        </label>

        <label>
          Password
          <input
            type="password"
            value={password}
            onChange={(event) => setPassword(event.target.value)}
            required
            autoComplete="current-password"
          />
        </label>

        {error && <p className="status-line error">{error}</p>}

        <button type="submit" disabled={loading}>
          {loading ? "Logging in..." : "Login"}
        </button>
      </form>

      <p className="auth-alt">
        Need an account? <Link to="/signup">Sign up</Link>
      </p>
    </section>
  );
}
