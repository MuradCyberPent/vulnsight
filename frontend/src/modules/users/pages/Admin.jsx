import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../../shared/api";
import SeverityBadge from "../../../shared/components/SeverityBadge";
import { fmtDate } from "../../../shared/util";

export const route = { path: "/admin", admin: true };
export const nav = { label: "Admin", order: 90, adminOnly: true };

export default function Admin() {
  const [users, setUsers] = useState([]);
  const [scans, setScans] = useState([]);
  const [error, setError] = useState("");

  useEffect(() => {
    Promise.all([api.adminUsers(), api.adminScans()])
      .then(([u, s]) => { setUsers(u); setScans(s); })
      .catch((e) => setError(e.message));
  }, []);

  return (
    <div className="space-y-10">
      <h1 className="text-3xl font-bold">Admin</h1>
      {error && <p role="alert" className="text-[#8C1A13]">{error}</p>}

      <section>
        <h2 className="mb-3 text-xl font-bold">Users ({users.length})</h2>
        <div className="panel overflow-x-auto">
          <table className="w-full min-w-[520px] text-left text-sm">
            <thead className="border-b border-line bg-paper text-muted"><tr>
              <th className="px-3 py-2 font-medium">Username</th><th className="px-3 py-2 font-medium">Email</th>
              <th className="px-3 py-2 font-medium">Role</th><th className="px-3 py-2 font-medium">Scans</th><th className="px-3 py-2 font-medium">Joined</th>
            </tr></thead>
            <tbody className="divide-y divide-line">
              {users.map((u) => (
                <tr key={u.id}><td className="px-3 py-2 font-medium">{u.username}</td><td className="px-3 py-2">{u.email}</td>
                  <td className="px-3 py-2">{u.role}</td><td className="px-3 py-2 font-mono">{u.scan_count}</td><td className="px-3 py-2 text-muted">{fmtDate(u.created_at)}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      <section>
        <h2 className="mb-3 text-xl font-bold">All scans ({scans.length})</h2>
        <div className="panel overflow-x-auto">
          <table className="w-full min-w-[520px] text-left text-sm">
            <thead className="border-b border-line bg-paper text-muted"><tr>
              <th className="px-3 py-2 font-medium">User</th><th className="px-3 py-2 font-medium">Target</th>
              <th className="px-3 py-2 font-medium">Risk</th><th className="px-3 py-2 font-medium">Date</th>
            </tr></thead>
            <tbody className="divide-y divide-line">
              {scans.map((s) => (
                <tr key={s.id}><td className="px-3 py-2">{s.owner_name}</td>
                  <td className="px-3 py-2 font-mono">{s.target}</td>
                  <td className="px-3 py-2">{s.status === "completed" ? <SeverityBadge level={s.risk_level} /> : <span className="capitalize text-muted">{s.status}</span>}</td>
                  <td className="px-3 py-2 text-muted">{fmtDate(s.started_at)}</td></tr>
              ))}
            </tbody>
          </table>
        </div>
        <p className="mt-2 text-xs text-muted">Admins can see which scans exist, but finding details stay private to their owner.</p>
      </section>
    </div>
  );
}
