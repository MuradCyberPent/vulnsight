import { usePrefs } from "../../../shared/auth";
import { SEV } from "../../../shared/util";
import SeverityBadge from "../../../shared/components/SeverityBadge";

export default function FindingCard({ f }) {
  const { beginner } = usePrefs();
  const s = SEV[f.severity] || SEV.Info;
  const openByDefault = beginner && (f.severity === "Critical" || f.severity === "High");

  return (
    <details open={openByDefault} className={`panel border-l-4 ${s.border} group`}>
      <summary className="flex cursor-pointer list-none items-start gap-3 px-4 py-3 hover:bg-paper">
        <SeverityBadge level={f.severity} className="mt-0.5 shrink-0" />
        <span className="min-w-0 flex-1">
          <span className="block font-medium">{f.title}</span>
          <span className="block text-xs text-muted">{f.category}</span>
        </span>
        <span className="mt-1 text-xs text-muted group-open:hidden">Show</span>
        <span className="mt-1 hidden text-xs text-muted group-open:inline">Hide</span>
      </summary>

      <div className="space-y-3 border-t border-line px-4 py-3 text-sm">
        {beginner && f.explanation && (
          <div className="rounded bg-teal-soft px-3 py-2">
            <p className="font-semibold text-teal-dark">What this means</p>
            <p>{f.explanation}</p>
          </div>
        )}
        {f.details && (
          <div>
            <p className="font-semibold">What we found</p>
            <pre className="mt-1 overflow-x-auto whitespace-pre-wrap break-words bg-paper px-3 py-2 font-mono text-xs">{f.details}</pre>
          </div>
        )}
        {f.fix && (
          <div>
            <p className="font-semibold">How to fix it</p>
            <p>{f.fix}</p>
          </div>
        )}
      </div>
    </details>
  );
}
