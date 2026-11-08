import { SEV } from "../util";

export default function SeverityBadge({ level, className = "" }) {
  const s = SEV[level] || SEV.Info;
  return (
    <span className={`inline-block rounded px-2 py-0.5 text-xs font-semibold ${s.badge} ${className}`}>
      {level}
    </span>
  );
}
