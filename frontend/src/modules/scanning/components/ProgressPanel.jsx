// The progress bar shown while a scan runs. (Member 1: Live Scan Progress)
export default function ProgressPanel({ scan }) {
  return (
          <div className="panel my-6 p-4" aria-live="polite">
            <p className="mb-2 text-sm font-medium">{scan.progress_text || "Starting..."}</p>
            <div className="h-2 bg-line" role="progressbar" aria-valuenow={scan.progress_pct} aria-valuemin={0} aria-valuemax={100}>
              <div className="h-2 bg-teal transition-all duration-500" style={{ width: `${Math.max(scan.progress_pct, 4)}%` }} />
            </div>
            <p className="mt-2 text-xs text-muted">Results appear below as each check finishes. You can leave this page; the scan keeps running.</p>
          </div>
  );
}
