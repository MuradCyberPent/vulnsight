import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../../../shared/auth";
import AuthShell from "../components/AuthShell";

export const route = { path: "/login", public: true };

export default function Login() {
  const { user, login } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to="/" replace />;

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await login(form.username, form.password);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  return (
    <AuthShell
      title="Log in"
      subtitle="Use your username or email."
      footer={<>New here? <Link to="/register" className="font-semibold text-teal underline">Create an account</Link></>}
    >
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label htmlFor="u" className="label">Username or email</label>
          <input id="u" className="field" autoComplete="username" required value={form.username}
                 onChange={(e) => setForm({ ...form, username: e.target.value })} />
        </div>
        <div>
          <label htmlFor="p" className="label">Password</label>
          <input id="p" type="password" className="field" autoComplete="current-password" required value={form.password}
                 onChange={(e) => setForm({ ...form, password: e.target.value })} />
        </div>
        {error && <p role="alert" className="bg-[#F9DEDC] px-3 py-2 text-sm text-[#8C1A13]">{error}</p>}
        <button className="btn-primary w-full" disabled={busy}>{busy ? "Logging in..." : "Log in"}</button>
      </form>
    </AuthShell>
  );
}
