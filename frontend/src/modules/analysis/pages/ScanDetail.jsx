import { useCallback, useEffect, useState } from "react";
import { Link, useNavigate, useParams } from "react-router-dom";
import { api } from "../../../shared/api";
import { usePrefs } from "../../../shared/auth";
import ProgressPanel from "../../scanning/components/ProgressPanel";
import FindingCard from "../components/FindingCard";
import ReportButtons from "../components/ReportButtons";
import RiskDial from "../components/RiskDial";
import { SEV, SEVERITIES, fmtDate, isRunning } from "../../../shared/util";

export const route = { path: "/scans/:id", priority: 10 };

export default function ScanDetail() {
  const { id } = useParams();
  const navigate = useNavigate();
  const { beginner, setBeginner } = usePrefs();
  const [scan, setScan] = useState(null);
  const [error, setError] = useState("");
  const [filter, setFilter] = useState("issues"); // issues | all | a severity name

  const load = useCallback(() => api.scan(id).then(setScan).catch((e) => setError(e.message)), [id]);

  useEffect(() => { setScan(null); load(); }, [load]);

  // Keep refreshing while the scan is running
  useEffect(() => {
    if (!isRunning(scan)) return;
    const t = setInterval(load, 1500);
    return () => clearInterval(t);
  }, [scan, load]);

  async function remove() {
    if (!window.confirm("Delete this scan and its findings?")) return;
    await api.deleteScan(id);
    navigate("/history");
  }

  if (error && !scan) return <p role="alert" className="text-[#8C1A13]">{error}</p>;
  if (!scan) return <p className="text-muted">Loading...</p>;

  const running = isRunning(scan);
  const shown = scan.findings.filter((f) =>
    filter === "all" ? true : filter === "issues" ? f.severity !== "Info" : f.severity === filter
  );
  const tabs = [
    ["issues", `Issues (${scan.findings.length - (scan.counts.Info || 0)})`],
    ...SEVERITIES.filter((s) => scan.counts[s] > 0).map((s) => [s, `${s} (${scan.counts[s]})`]),
    ["all", `Everything (${scan.findings.length})`],
  ];

  return (
    <div>
      <p className="mb-2 text-sm"><Link to="/history" className="text-teal underline">History</Link> / Scan {scan.id}</p>
      <div className="flex flex-wrap items-start justify-between gap-6">
        <div className="min-w-0">
          <h1 className="break-all font-mono text-2xl font-bold md:text-3xl">{scan.target}</h1>
          <p className="mt-1 text-sm text-muted">
            {scan.resolved_ip} &middot; {scan.profile} profile &middot; {fmtDate(scan.started_at)}
            {scan.ports_spec ? ` · ports ${scan.ports_spec}` : ""}
          </p>
        </div>
        {!running && scan.status === "completed" && <RiskDial score={scan.risk_score} level={scan.risk_level} />}
      </div>

      {running && <ProgressPanel scan={scan} />}

      {scan.status === "failed" && (
        <p role="alert" className="my-6 bg-[#F9DEDC] px-3 py-2 text-sm text-[#8C1A13]">
          This scan failed{scan.error ? `: ${scan.error}` : "."} Try running it again.
        </p>
      )}
      {error && <p role="alert" className="my-3 text-sm text-[#8C1A13]">{error}</p>}

      <div className="my-6 flex flex-wrap items-center justify-between gap-3 border-y border-line py-3">
        <label className="flex cursor-pointer items-center gap-2 text-sm">
          <input type="checkbox" className="accent-[#0E7C86]" checked={beginner} onChange={(e) => setBeginner(e.target.checked)} />
          <span><span className="font-semibold">Beginner mode</span> <span className="text-muted">(explain each finding in plain English)</span></span>
        </label>
        {!running && (
          <div className="flex flex-wrap gap-2">
            <ReportButtons scanId={id} onError={setError} />
            <button className="btn-danger" onClick={remove}>Delete</button>
          </div>
        )}
      </div>

      <div className="mb-4 flex flex-wrap gap-2" role="tablist" aria-label="Filter findings">
        {tabs.map(([key, label]) => (
          <button
            key={key} role="tab" aria-selected={filter === key}
            onClick={() => setFilter(key)}
            className={`rounded-full border px-3 py-1 text-sm ${filter === key ? "border-ink bg-ink text-white" : "border-line bg-white hover:bg-paper"}`}
          >
            {SEV[key] && <span className={`mr-1.5 inline-block h-2 w-2 rounded-full ${SEV[key].bar}`} />}
            {label}
          </button>
        ))}
      </div>

      {shown.length === 0 ? (
        <p className="panel p-6 text-muted">
          {running ? "Nothing found yet..." : filter === "issues" ? "No issues found in this scan. Switch to Everything to see the informational results." : "Nothing in this category."}
        </p>
      ) : (
        <div className="space-y-2">{shown.map((f) => <FindingCard key={f.id} f={f} />)}</div>
      )}
    </div>
  );
}
