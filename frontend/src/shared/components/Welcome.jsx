import { useAuth } from "../auth";

// Shown at "/" only while no module provides a home page yet.
export default function Welcome() {
  const { user } = useAuth();
  return (
    <div className="max-w-xl">
      <h1 className="text-3xl font-bold">Welcome, {user.username}</h1>
      <p className="mt-2 text-muted">Your account is ready. More features appear here as their modules are installed.</p>
    </div>
  );
}
