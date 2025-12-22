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
    <div className="flex min-h-screen flex-col items-center justify-center bg-gradient-to-br from-shadow-black via-arcane-blue-900/20 to-shadow-black p-6">
      <div className="parchment-card w-full max-w-md p-8">
        <div className="mb-6 text-center">
          <div className="mb-3 text-5xl font-display text-forest-green-800">🛡</div>
          <h1 className="text-3xl font-display font-bold text-arcane-blue-900">Forge your adventurer profile</h1>
          <p className="mt-2 text-sm text-gray-700">Begin your legendary journey</p>
        </div>
        <form className="space-y-5" onSubmit={handleSubmit}>
          <label className="block text-sm font-display font-semibold text-arcane-blue-800">
            Email
            <input
              className="fantasy-input mt-2 w-full"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>
          <label className="block text-sm font-display font-semibold text-arcane-blue-800">
            Username
            <input
              className="fantasy-input mt-2 w-full"
              value={username}
              onChange={(event) => setUsername(event.target.value)}
              required
            />
          </label>
          <label className="block text-sm font-display font-semibold text-arcane-blue-800">
            Display Name
            <input
              className="fantasy-input mt-2 w-full"
              value={displayName}
              onChange={(event) => setDisplayName(event.target.value)}
              required
            />
          </label>
          <label className="block text-sm font-display font-semibold text-arcane-blue-800">
            Password
            <input
              className="fantasy-input mt-2 w-full"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
              minLength={8}
            />
          </label>
          {error ? (
            <div className="rounded-md border-2 border-ember-red-600 bg-ember-red-50 p-3">
              <p className="text-sm font-medium text-ember-red-800">{error}</p>
            </div>
          ) : null}
          <button
            className="fantasy-button w-full bg-gradient-to-b from-forest-green-700 to-forest-green-900 hover:from-forest-green-600 hover:to-forest-green-800 disabled:opacity-50"
            disabled={isSubmitting}
            type="submit"
          >
            {isSubmitting ? "Forging your path..." : "Create Account"}
          </button>
        </form>
        <p className="mt-6 text-center text-sm text-gray-700">
          Already have an account?{" "}
          <Link className="font-display font-semibold text-arcane-blue-800 hover:text-arcane-blue-600 hover:underline" to="/login">
            Return to the realm
          </Link>
        </p>
      </div>
    </div>
  );
}

export default Register;

