import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { api } from "../../../shared/api";
import CountChips from "../../../shared/components/CountChips";
import SeverityBadge from "../../../shared/components/SeverityBadge";
import { fmtDate } from "../../../shared/util";

export const route = { path: "/history" };
export const nav = { label: "History", order: 30 };

export default function History() {
  const navigate = useNavigate();
  const [scans, setScans] = useState(null);
  const [picked, setPicked] = useState([]);
  const [error, setError] = useState("");

  const load = () => api.scans().then(setScans).catch((e) => setError(e.message));
  useEffect(() => { load(); }, []);

  function toggle(id) {
    setPicked((p) => (p.includes(id) ? p.filter((x) => x !== id) : [...p, id].slice(-2)));
  }

  async function remove(id) {
    if (!window.confirm("Delete this scan and its findings? This cannot be undone.")) return;
    try {
      await api.deleteScan(id);
      setPicked((p) => p.filter((x) => x !== id));
      load();
    } catch (e) { setError(e.message); }
  }

  function compare() {
    const [a, b] = [...picked].sort((x, y) => x - y);
    navigate(`/compare?a=${a}&b=${b}`);
  }

  if (!scans) return <p className="text-muted">{error || "Loading..."}</p>;

  return (
    <div>
      <div className="mb-6 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold">History</h1>
          <p className="mt-1 text-muted">Tick two scans to see what changed between them.</p>
        </div>
        <button className="btn-quiet" disabled={picked.length !== 2} onClick={compare}>Compare selected</button>
      </div>
      {error && <p role="alert" className="mb-4 text-[#8C1A13]">{error}</p>}

      {scans.length === 0 ? (
        <div className="panel p-8">
          <p className="mb-4 text-muted">No scans yet. Every scan you run is saved here so you can track your progress.</p>
          <Link to="/scan/new" className="btn-primary">Run a scan</Link>
        </div>
      ) : (
        <div className="panel overflow-x-auto">
          <table className="w-full min-w-[640px] text-left text-sm">
            <thead className="border-b border-line bg-paper text-muted">
              <tr>
                <th className="w-10 px-3 py-2"><span className="sr-only">Select</span></th>
                <th className="px-3 py-2 font-medium">Target</th>
                <th className="px-3 py-2 font-medium">Risk</th>
                <th className="px-3 py-2 font-medium">Issues</th>
                <th className="px-3 py-2 font-medium">Date</th>
                <th className="px-3 py-2"><span className="sr-only">Actions</span></th>
              </tr>
            </thead>
            <tbody className="divide-y divide-line">
              {scans.map((s) => (
                <tr key={s.id} className="hover:bg-paper/60">
                  <td className="px-3 py-2.5">
                    <input type="checkbox" aria-label={`Select scan ${s.id} of ${s.target}`} className="accent-[#0E7C86]"
                           checked={picked.includes(s.id)} disabled={s.status !== "completed"} onChange={() => toggle(s.id)} />
                  </td>
                  <td className="px-3 py-2.5">
                    <Link to={`/scans/${s.id}`} className="font-mono font-medium text-teal underline">{s.target}</Link>
                    <span className="ml-2 text-xs text-muted">{s.profile}</span>
                  </td>
                  <td className="px-3 py-2.5">
                    {s.status === "completed" ? (
                      <span className="flex items-center gap-2"><span className="font-mono">{s.risk_score}</span><SeverityBadge level={s.risk_level} /></span>
                    ) : <span className="capitalize text-muted">{s.status}</span>}
                  </td>
                  <td className="px-3 py-2.5"><CountChips counts={s.counts} /></td>
                  <td className="px-3 py-2.5 text-muted">{fmtDate(s.started_at)}</td>
                  <td className="px-3 py-2.5 text-right">
                    <button className="text-sm text-[#8C1A13] underline" onClick={() => remove(s.id)}>Delete</button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}
