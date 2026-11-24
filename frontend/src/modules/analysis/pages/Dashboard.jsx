import { useEffect, useState } from "react";
import { Link } from "react-router-dom";
import { api } from "../../../shared/api";
import { useAuth } from "../../../shared/auth";
import CountChips from "../../../shared/components/CountChips";
import SeverityBadge from "../../../shared/components/SeverityBadge";
import { SEV, SEVERITIES, fmtDate } from "../../../shared/util";

export const route = { path: "/" };
export const nav = { label: "Dashboard", order: 10, end: true };

export default function Dashboard() {
  const { user } = useAuth();
  const [stats, setStats] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => { api.stats().then(setStats).catch((e) => setError(e.message)); }, []);

  if (error) return <p role="alert" className="text-[#8C1A13]">{error}</p>;
  if (!stats) return <p className="text-muted">Loading...</p>;

  if (stats.total_scans === 0) {
    return (
      <div className="max-w-xl">
        <h1 className="text-3xl font-bold">Welcome, {user.username}</h1>
        <p className="mb-6 mt-2 text-muted">
          You have not scanned anything yet. Your first scan takes under a minute and ends with a plain-English list of what to fix.
        </p>
        <Link to="/scan/new" className="btn-primary">Run your first scan</Link>
      </div>
    );
  }

  const open = stats.open_findings;
  const maxOpen = Math.max(1, ...SEVERITIES.filter((s) => s !== "Info").map((s) => open[s]));

  return (
    <div>
      <div className="mb-8 flex flex-wrap items-end justify-between gap-3">
        <div>
          <h1 className="text-3xl font-bold">Welcome back, {user.username}</h1>
          <p className="mt-1 text-muted">Based on the latest scan of each target.</p>
        </div>
        <Link to="/scan/new" className="btn-primary">New scan</Link>
      </div>

      <dl className="mb-10 grid grid-cols-3 divide-x divide-line border-y border-line py-4 text-center">
        <div><dd className="font-display text-3xl font-bold">{stats.total_scans}</dd><dt className="text-sm text-muted">Scans run</dt></div>
        <div><dd className="font-display text-3xl font-bold">{stats.targets}</dd><dt className="text-sm text-muted">Targets</dt></div>
        <div><dd className="font-display text-3xl font-bold">{stats.average_risk}</dd><dt className="text-sm text-muted">Average risk score</dt></div>
      </dl>

      <div className="grid gap-10 md:grid-cols-2">
        <section>
          <h2 className="mb-3 text-xl font-bold">Open issues by severity</h2>
          <ul className="space-y-2">
            {SEVERITIES.filter((s) => s !== "Info").map((s) => (
              <li key={s} className="flex items-center gap-3 text-sm">
                <span className="w-16 font-medium">{s}</span>
                <span className="h-3 flex-1 bg-line">
                  <span className={`block h-3 ${SEV[s].bar}`} style={{ width: `${(open[s] / maxOpen) * 100}%` }} />
                </span>
                <span className="w-6 text-right font-mono">{open[s]}</span>
              </li>
            ))}
          </ul>
        </section>

        <section>
          <h2 className="mb-3 text-xl font-bold">Riskiest targets</h2>
          <ul className="divide-y divide-line border-y border-line">
            {stats.latest_by_target.map((t) => (
              <li key={t.scan_id}>
                <Link to={`/scans/${t.scan_id}`} className="flex items-center justify-between gap-3 py-2.5 hover:bg-white">
                  <span className="truncate font-mono text-sm">{t.target}</span>
                  <span className="flex items-center gap-2">
                    <span className="font-mono text-sm">{t.risk_score}</span>
                    <SeverityBadge level={t.risk_level} />
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </section>
      </div>

      <section className="mt-10">
        <div className="mb-3 flex items-baseline justify-between">
          <h2 className="text-xl font-bold">Recent scans</h2>
          <Link to="/history" className="text-sm font-semibold text-teal underline">See all</Link>
        </div>
        <ul className="panel divide-y divide-line">
          {stats.recent.map((s) => (
            <li key={s.id}>
              <Link to={`/scans/${s.id}`} className="flex flex-wrap items-center justify-between gap-2 px-4 py-3 hover:bg-paper">
                <span>
                  <span className="font-mono text-sm font-medium">{s.target}</span>
                  <span className="ml-2 text-xs text-muted">{fmtDate(s.started_at)}</span>
                </span>
                {s.status === "completed" ? <CountChips counts={s.counts} /> : <span className="text-sm text-muted capitalize">{s.status}</span>}
              </Link>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
