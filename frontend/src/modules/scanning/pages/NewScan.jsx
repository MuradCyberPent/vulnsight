import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../../../shared/api";

export const route = { path: "/scan/new" };
export const nav = { label: "New scan", order: 20 };

export default function NewScan() {
  const navigate = useNavigate();
  const [profiles, setProfiles] = useState([]);
  const [target, setTarget] = useState("");
  const [profile, setProfile] = useState("quick");
  const [ports, setPorts] = useState("");
  const [authorized, setAuthorized] = useState(false);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  useEffect(() => { api.profiles().then(setProfiles).catch((e) => setError(e.message)); }, []);

  async function submit(e) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      const scan = await api.startScan({ target, profile, ports: profile === "web-only" ? null : ports || null, authorized });
      navigate(`/scans/${scan.id}`);
    } catch (err) {
      setError(err.message);
      setBusy(false);
    }
  }

  return (
    <div className="max-w-2xl">
      <h1 className="text-3xl font-bold">New scan</h1>
      <p className="mb-8 mt-1 text-muted">Enter a domain or IP address. One target per scan.</p>

      <form onSubmit={submit} className="space-y-7">
        <div>
          <label htmlFor="target" className="label">Target</label>
          <input id="target" className="field font-mono" placeholder="example.com or 203.0.113.10" required
                 value={target} onChange={(e) => setTarget(e.target.value)} autoFocus />
          <p className="mt-1 text-xs text-muted">Safe places to practise: scanme.nmap.org, or your own lab (like DVWA).</p>
        </div>

        <fieldset>
          <legend className="label">Scan profile</legend>
          <div className="panel divide-y divide-line">
            {profiles.map((p) => (
              <label key={p.id} className={`flex cursor-pointer items-start gap-3 px-4 py-3 ${profile === p.id ? "bg-teal-soft" : "hover:bg-paper"}`}>
                <input type="radio" name="profile" className="mt-1 accent-[#0E7C86]" checked={profile === p.id} onChange={() => setProfile(p.id)} />
                <span>
                  <span className="block font-semibold">{p.label}</span>
                  <span className="block text-sm text-muted">{p.description}</span>
                </span>
              </label>
            ))}
          </div>
        </fieldset>

        {profile !== "web-only" && (
          <details className="panel px-4 py-3">
            <summary className="cursor-pointer text-sm font-medium">Choose your own ports (optional)</summary>
            <div className="mt-3">
              <label htmlFor="ports" className="label">Ports</label>
              <input id="ports" className="field font-mono" placeholder="22,80,443 or 1-1024" value={ports} onChange={(e) => setPorts(e.target.value)} />
              <p className="mt-1 text-xs text-muted">Leave empty to use the profile's default ports. Maximum 2000 ports.</p>
            </div>
          </details>
        )}

        <label className="panel flex cursor-pointer items-start gap-3 px-4 py-3">
          <input type="checkbox" className="mt-1 accent-[#0E7C86]" checked={authorized} onChange={(e) => setAuthorized(e.target.checked)} />
          <span className="text-sm">
            <span className="block font-semibold">I own this target or have written permission to test it.</span>
            <span className="text-muted">Scanning systems without permission can be illegal. Every scan is saved with this confirmation.</span>
          </span>
        </label>

        {error && <p role="alert" className="bg-[#F9DEDC] px-3 py-2 text-sm text-[#8C1A13]">{error}</p>}
        <button className="btn-primary" disabled={busy || !authorized || !target.trim()}>
          {busy ? "Starting..." : "Start scan"}
        </button>
      </form>
    </div>
  );
}
