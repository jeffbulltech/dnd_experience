import { FormEvent, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { useAuth } from "../contexts/AuthContext";

function Register(): JSX.Element {
  const { register } = useAuth();
  const navigate = useNavigate();

  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setSubmitting] = useState(false);

  const handleSubmit = async (event: FormEvent<HTMLFormElement>) => {
    event.preventDefault();
    setError(null);
    try {
      setSubmitting(true);
      await register({
        email,
        username,
        display_name: displayName,
        password
      });
      navigate("/campaigns", { replace: true });
    } catch (err) {
      console.error(err);
      setError("Unable to register. Please check your details and try again.");
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-parchment/80 p-6">
      <div className="w-full max-w-md rounded-lg border border-arcane-blue/40 bg-white/90 p-6 shadow">
        <h1 className="mb-4 text-2xl font-serif text-arcane-blue">Forge your adventurer profile</h1>
        <form className="space-y-4" onSubmit={handleSubmit}>
          <label className="block text-sm font-semibold text-arcane-blue">
            Email
            <input
              className="mt-1 w-full rounded border border-gray-300 p-2 text-sm focus:border-arcane-blue focus:outline-none"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>
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
            Display Name
            <input
              className="mt-1 w-full rounded border border-gray-300 p-2 text-sm focus:border-arcane-blue focus:outline-none"
              value={displayName}
              onChange={(event) => setDisplayName(event.target.value)}
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
              minLength={8}
            />
          </label>
          {error ? <p className="text-sm text-ember-red">{error}</p> : null}
          <button
            className="w-full rounded bg-forest-green px-4 py-2 text-sm font-semibold text-white hover:bg-forest-green/90 disabled:opacity-50"
            disabled={isSubmitting}
            type="submit"
          >
            {isSubmitting ? "Registering..." : "Create Account"}
          </button>
        </form>
        <p className="mt-4 text-sm text-gray-600">
          Already have an account?{" "}
          <Link className="text-arcane-blue hover:underline" to="/login">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}

export default Register;

