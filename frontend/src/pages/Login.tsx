import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";

function Login(): JSX.Element {
  const { login } = useAuth();
  const navigate = useNavigate();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    try {
      setSubmitting(true);
      await login(username, password);
      navigate("/campaigns", { replace: true });
    } catch (err) {
      console.error(err);
      setError("Invalid credentials, please try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-parchment/80 p-6">
      <div className="w-full max-w-md rounded-lg border border-arcane-blue/40 bg-white/90 p-6 shadow">
        <h1 className="mb-4 text-2xl font-serif text-arcane-blue">Welcome back, adventurer</h1>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <label className="block text-sm font-semibold text-arcane-blue">
            Username
            <input
              className="mt-1 w-full rounded border border-gray-300 p-2 text-sm focus:border-arcane-blue focus:outline-none"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
            />
          </label>
          <label className="block text-sm font-semibold text-arcane-blue">
            Password
            <input
              className="mt-1 w-full rounded border border-gray-300 p-2 text-sm focus:border-arcane-blue focus:outline-none"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>
          {error ? <p className="text-sm text-ember-red">{error}</p> : null}
          <button
            className="w-full rounded bg-arcane-blue px-4 py-2 text-sm font-semibold text-white hover:bg-arcane-blue/90 disabled:opacity-50"
            disabled={isSubmitting}
            type="submit"
          >
            {isSubmitting ? "Signing in..." : "Sign In"}
          </button>
        </form>
        <p className="mt-4 text-sm text-gray-600">
          Need an account?{" "}
          <Link className="text-arcane-blue hover:underline" to="/register">
            Register here
          </Link>
        </p>
      </div>
    </div>
  );
}

export default Login;

