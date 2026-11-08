import { SEV, SEVERITIES } from "../util";

// Small coloured counts like  2 Critical  1 High
export default function CountChips({ counts }) {
  const shown = SEVERITIES.filter((s) => s !== "Info" && counts?.[s] > 0);
  if (!shown.length) return <span className="text-sm text-muted">No issues</span>;
  return (
    <span className="flex flex-wrap gap-1">
      {shown.map((s) => (
        <span key={s} className={`rounded px-1.5 py-0.5 text-xs font-semibold ${SEV[s].badge}`}>
          {counts[s]} {s}
        </span>
      ))}
    </span>
  );
}
