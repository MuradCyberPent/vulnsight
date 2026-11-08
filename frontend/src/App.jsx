import { Navigate, Route, Routes } from "react-router-dom";
import Layout from "./shared/components/Layout";
import Welcome from "./shared/components/Welcome";
import { useAuth } from "./shared/auth";
import { pages } from "./shared/pageRegistry";

function Protected({ children, admin = false }) {
  const { user, loading } = useAuth();
  if (loading) return <p className="p-8 text-muted">Loading...</p>;
  if (!user) {
    // Before Module 1 is installed there is no login page yet; avoid redirecting forever.
    return pages.some((p) => p.path === "/login")
      ? <Navigate to="/login" replace />
      : <p className="p-8 text-muted">The login page is not installed yet (it comes with Module 1).</p>;
  }
  if (admin && user.role !== "admin") return <Navigate to="/" replace />;
  return <Layout>{children}</Layout>;
}

// Routes are built from the pages found in src/modules (see shared/pageRegistry.js).
export default function App() {
  const hasHome = pages.some((p) => p.path === "/");
  return (
    <Routes>
      {pages.map(({ path, Component, public: isPublic, admin }) => (
        <Route
          key={path}
          path={path}
          element={isPublic ? <Component /> : <Protected admin={admin}><Component /></Protected>}
        />
      ))}
      {!hasHome && <Route path="/" element={<Protected><Welcome /></Protected>} />}
      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
