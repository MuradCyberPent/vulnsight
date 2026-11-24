import { useEffect, useState } from "react";
import { Link, useSearchParams } from "react-router-dom";
import { api } from "../../../shared/api";
import SeverityBadge from "../../../shared/components/SeverityBadge";
import { fmtDate } from "../../../shared/util";

function Column({ title, hint, items, empty }) {
  return (
    <section>
      <h2 className="text-xl font-bold">{title} <span className="font-mono text-base text-muted">{items.length}</span></h2>
      <p className="mb-2 text-sm text-muted">{hint}</p>
      {items.length === 0 ? (
        <p className="panel p-4 text-sm text-muted">{empty}</p>
      ) : (
        <ul className="panel divide-y divide-line">
          {items.map((i) => (
            <li key={i.category + i.key} className="flex items-start gap-3 px-4 py-2.5 text-sm">
              <SeverityBadge level={i.severity} className="mt-0.5 shrink-0" />
              <span>{i.title}<span className="block text-xs text-muted">{i.category}</span></span>
            </li>
          ))}
        </ul>
      )}
    </section>
  );
}

export const route = { path: "/compare" };
export const nav = { label: "Compare", order: 40 };

export default function Compare() {
  const [params, setParams] = useSearchParams();
  const a = params.get("a");
  const b = params.get("b");
  const [scans, setScans] = useState([]);
  const [pickA, setPickA] = useState(a || "");
  const [pickB, setPickB] = useState(b || "");
  const [result, setResult] = useState(null);
  const [error, setError] = useState("");

  useEffect(() => { api.scans().then((s) => setScans(s.filter((x) => x.status === "completed"))).catch((e) => setError(e.message)); }, []);

  useEffect(() => {
    setResult(null);
    if (a && b) api.compare(a, b).then(setResult).catch((e) => setError(e.message));
  }, [a, b]);

  function go(e) {
    e.preventDefault();
    setError("");
    const [x, y] = [Number(pickA), Number(pickB)].sort((m, n) => m - n);
    setParams({ a: x, b: y });
  }

  const label = (s) => `#${s.id} ${s.target} (${fmtDate(s.started_at)})`;

  return (
    <div>
      <h1 className="text-3xl font-bold">Compare scans</h1>
      <p className="mb-6 mt-1 text-muted">See what is new, what you fixed, and what is still open between two scans.</p>

      <form onSubmit={go} className="mb-8 flex flex-wrap items-end gap-3">
        {[["Older scan", pickA, setPickA], ["Newer scan", pickB, setPickB]].map(([name, val, set]) => (
          <div key={name} className="min-w-[14rem] flex-1">
            <label className="label">{name}</label>
            <select className="field" required value={val} onChange={(e) => set(e.target.value)}>
              <option value="">Choose a scan...</option>
              {scans.map((s) => <option key={s.id} value={s.id}>{label(s)}</option>)}
            </select>
          </div>
        ))}
        <button className="btn-primary" disabled={!pickA || !pickB || pickA === pickB}>Compare</button>
      </form>

      {error && <p role="alert" className="mb-4 text-[#8C1A13]">{error}</p>}
      {scans.length < 2 && !error && (
        <p className="panel p-6 text-muted">You need at least two finished scans to compare. <Link to="/scan/new" className="text-teal underline">Run a scan</Link></p>
      )}

      {result && (
        <>
          <div className="mb-8 flex flex-wrap items-baseline gap-x-8 gap-y-2 border-y border-line py-4">
            <p>
              <span className="text-sm text-muted">Risk score </span>
              <span className="font-mono text-lg">{result.scan_a.risk_score}</span>
              <span className="text-muted"> to </span>
              <span className="font-mono text-lg">{result.scan_b.risk_score}</span>
            </p>
            <p className={`font-display text-2xl font-bold ${result.score_change > 0 ? "text-[#B3261E]" : result.score_change < 0 ? "text-[#2F7D5B]" : "text-muted"}`}>
              {result.score_change > 0 ? `Worse by ${result.score_change}` : result.score_change < 0 ? `Better by ${-result.score_change}` : "No change"}
            </p>
            <p className="text-sm text-muted">{result.scan_a.target} vs {result.scan_b.target}</p>
          </div>
          {result.scan_a.profile !== result.scan_b.profile && (
            <p role="note" className="mb-6 bg-[#FBF1D6] px-3 py-2 text-sm text-[#6F4D00]">
              These scans used different profiles ({result.scan_a.profile} and {result.scan_b.profile}), so some items under
              Fixed or New may simply not have been checked in one of them. For a fair comparison, use the same profile both times.
            </p>
          )}
          <div className="grid gap-8 lg:grid-cols-3">
            <Column title="New" hint="Appeared since the older scan." items={result.new} empty="Nothing new. Nice." />
            <Column title="Fixed" hint="Gone since the older scan." items={result.fixed} empty="Nothing fixed yet." />
            <Column title="Still open" hint="Present in both scans." items={result.unchanged} empty="Nothing carried over." />
          </div>
          <p className="mt-6 text-xs text-muted">Informational results are left out of comparisons.</p>
        </>
      )}
    </div>
  );
}
