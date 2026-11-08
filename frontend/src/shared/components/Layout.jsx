import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../auth";
import { navItems } from "../pageRegistry";
import Logo from "./Logo";

const link = ({ isActive }) =>
  `block rounded-md px-3 py-2 text-sm font-medium whitespace-nowrap ${
    isActive ? "bg-white/15 text-white" : "text-white/70 hover:bg-white/10 hover:text-white"
  }`;

export default function Layout({ children }) {
  const { user, logout } = useAuth();
  const navigate = useNavigate();

  // Menu entries come from the pages themselves (each page exports `nav`), so no shared list to edit.
  const items = navItems
    .filter((i) => !i.adminOnly || user.role === "admin")
    .map((i) => [i.to, i.label, i.end]);

  return (
    <div className="min-h-screen md:flex">
      <aside className="bg-ink text-white md:fixed md:inset-y-0 md:flex md:w-56 md:flex-col md:justify-between md:p-4">
        <div>
          <div className="flex items-center justify-between px-4 py-3 md:px-3 md:pb-6 md:pt-2">
            <Logo light />
            <button
              className="text-sm text-white/70 hover:text-white md:hidden"
              onClick={() => { logout(); navigate("/login"); }}
            >
              Log out
            </button>
          </div>
          <nav className="flex gap-1 overflow-x-auto px-3 pb-3 md:flex-col md:overflow-visible md:p-0" aria-label="Main">
            {items.map(([to, label, end]) => (
              <NavLink key={to} to={to} end={end} className={link}>{label}</NavLink>
            ))}
          </nav>
        </div>
        <div className="hidden border-t border-white/15 px-3 pt-4 md:block">
          <p className="truncate text-sm font-medium">{user.username}</p>
          <p className="mb-3 truncate text-xs text-white/60">{user.role === "admin" ? "Administrator" : user.email}</p>
          <button className="text-sm text-white/70 hover:text-white" onClick={() => { logout(); navigate("/login"); }}>
            Log out
          </button>
        </div>
      </aside>
      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-6 md:ml-56 md:px-8 md:py-10">{children}</main>
    </div>
  );
}
