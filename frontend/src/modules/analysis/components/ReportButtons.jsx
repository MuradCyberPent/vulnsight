import { api } from "../../../shared/api";

// Download buttons for the HTML, JSON and TXT report. (Member 1: Report Export)
export default function ReportButtons({ scanId, onError }) {
  async function download(format) {
    try { await api.downloadReport(scanId, format); } catch (e) { onError?.(e.message); }
  }
  return (
    <>
      {["html", "json", "txt"].map((f) => (
        <button key={f} className="btn-quiet" onClick={() => download(f)}>Download {f.toUpperCase()}</button>
      ))}
    </>
  );
}
