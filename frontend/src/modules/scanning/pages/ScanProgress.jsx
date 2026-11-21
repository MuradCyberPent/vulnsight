import { useCallback, useEffect, useState } from "react";
import { useParams } from "react-router-dom";
import { api } from "../../../shared/api";
import SeverityBadge from "../../../shared/components/SeverityBadge";
import { fmtDate, isRunning } from "../../../shared/util";
import ProgressPanel from "../components/ProgressPanel";

// Basic scan page: live progress, then a plain list of findings. (Member 1)
// When Module 3 is installed, its richer ScanDetail page (priority 10) takes over this address.
export const route = { path: "/scans/:id", priority: 0 };

export default function ScanProgress() {
  const { id } = useParams();
  const [scan, setScan] = useState(null);
  const [error, setError] = useState("");

  const load = useCallback(() => api.scan(id).then(setScan).catch((e) => setError(e.message)), [id]);
  useEffect(() => { setScan(null); load(); }, [load]);
  useEffect(() => {
    if (!isRunning(scan)) return;
    const t = setInterval(load, 1500);
    return () => clearInterval(t);
  }, [scan, load]);

  if (error && !scan) return <p role="alert" className="text-[#8C1A13]">{error}</p>;
  if (!scan) return <p className="text-muted">Loading...</p>;

  return (
    <div>
      <h1 className="break-all font-mono text-2xl font-bold md:text-3xl">{scan.target}</h1>
      <p className="mt-1 text-sm text-muted">{scan.resolved_ip} &middot; {scan.profile} profile &middot; {fmtDate(scan.started_at)}</p>
      {isRunning(scan) && <ProgressPanel scan={scan} />}
      {scan.status === "failed" && (
        <p role="alert" className="my-6 bg-[#F9DEDC] px-3 py-2 text-sm text-[#8C1A13]">This scan failed{scan.error ? `: ${scan.error}` : "."}</p>
      )}
      <ul className="panel mt-6 divide-y divide-line">
        {scan.findings.map((f) => (
          <li key={f.id} className="flex items-start gap-3 px-4 py-2.5 text-sm">
            <SeverityBadge level={f.severity} className="mt-0.5 shrink-0" />
            <span>{f.title}<span className="block text-xs text-muted">{f.category}</span></span>
          </li>
        ))}
        {scan.findings.length === 0 && <li className="px-4 py-3 text-muted">No findings yet.</li>}
      </ul>
    </div>
  );
}
