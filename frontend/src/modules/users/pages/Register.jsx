import { useState } from "react";
import { Link, Navigate, useNavigate } from "react-router-dom";
import { useAuth } from "../../../shared/auth";
import AuthShell from "../components/AuthShell";

export const route = { path: "/register", public: true };

export default function Register() {
  const { user, register } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: "", email: "", password: "" });
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  if (user) return <Navigate to="/" replace />;

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      await register(form);
      navigate("/");
    } catch (err) {
      setError(err.message);
    } finally {
      setBusy(false);
    }
  }

  const set = (k) => (e) => setForm({ ...form, [k]: e.target.value });

  return (
    <AuthShell
      title="Create your account"
      subtitle="Your scans and reports stay private to you."
      footer={<>Already registered? <Link to="/login" className="font-semibold text-teal underline">Log in</Link></>}
    >
      <form onSubmit={submit} className="space-y-4">
        <div>
          <label htmlFor="un" className="label">Username</label>
          <input id="un" className="field" required minLength={3} maxLength={30} pattern="[A-Za-z0-9_.\-]+"
                 title="Letters, numbers, dot, dash and underscore" autoComplete="username" value={form.username} onChange={set("username")} />
        </div>
        <div>
          <label htmlFor="em" className="label">Email</label>
          <input id="em" type="email" className="field" required autoComplete="email" value={form.email} onChange={set("email")} />
        </div>
        <div>
          <label htmlFor="pw" className="label">Password</label>
          <input id="pw" type="password" className="field" required minLength={8} maxLength={64}
                 autoComplete="new-password" value={form.password} onChange={set("password")} />
          <p className="mt-1 text-xs text-muted">8 to 64 characters. It is stored as a bcrypt hash, never as plain text.</p>
        </div>
        {error && <p role="alert" className="bg-[#F9DEDC] px-3 py-2 text-sm text-[#8C1A13]">{error}</p>}
        <button className="btn-primary w-full" disabled={busy}>{busy ? "Creating account..." : "Create account"}</button>
      </form>
    </AuthShell>
  );
}
