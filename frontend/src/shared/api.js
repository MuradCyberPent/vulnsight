// All talking to the backend happens here.
const BASE = import.meta.env.VITE_API_URL || "http://localhost:8000";
const TOKEN_KEY = "vulnsight_token";

export const getToken = () => localStorage.getItem(TOKEN_KEY);
export const setToken = (t) => localStorage.setItem(TOKEN_KEY, t);
export const clearToken = () => localStorage.removeItem(TOKEN_KEY);

function messageFrom(data, status) {
  const d = data?.detail;
  if (typeof d === "string") return d;
  if (Array.isArray(d) && d.length) {
    const first = d[0];
    const field = first.loc?.[first.loc.length - 1];
    return field ? `${field}: ${first.msg}` : first.msg;
  }
  return `Something went wrong (error ${status}).`;
}

async function request(path, { method = "GET", body, form, raw = false } = {}) {
  const headers = {};
  const token = getToken();
  if (token) headers.Authorization = `Bearer ${token}`;
  let payload;
  if (form) {
    payload = new URLSearchParams(form);
  } else if (body) {
    headers["Content-Type"] = "application/json";
    payload = JSON.stringify(body);
  }

  let res;
  try {
    res = await fetch(BASE + path, { method, headers, body: payload });
  } catch {
    throw new Error("Cannot reach the server. Is the backend running?");
  }

  if (res.status === 401 && token && !path.startsWith("/api/auth/login")) {
    clearToken();
    window.location.href = "/login";
    throw new Error("Please log in again.");
  }
  if (!res.ok) {
    let data = null;
    try { data = await res.json(); } catch { /* not JSON */ }
    throw new Error(messageFrom(data, res.status));
  }
  if (raw) return res;
  if (res.status === 204) return null;
  return res.json();
}

export const api = {
  register: (data) => request("/api/auth/register", { method: "POST", body: data }),
  login: (username, password) => request("/api/auth/login", { method: "POST", form: { username, password } }),
  me: () => request("/api/auth/me"),
  profiles: () => request("/api/profiles"),
  startScan: (data) => request("/api/scans", { method: "POST", body: data }),
  scans: () => request("/api/scans"),
  scan: (id) => request(`/api/scans/${id}`),
  deleteScan: (id) => request(`/api/scans/${id}`, { method: "DELETE" }),
  compare: (a, b) => request(`/api/scans/compare?a=${a}&b=${b}`),
  stats: () => request("/api/stats"),
  adminUsers: () => request("/api/admin/users"),
  adminScans: () => request("/api/admin/scans"),

  async downloadReport(id, format) {
    const res = await request(`/api/scans/${id}/report?format=${format}`, { raw: true });
    const blob = await res.blob();
    const match = /filename="([^"]+)"/.exec(res.headers.get("Content-Disposition") || "");
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = match ? match[1] : `vulnsight-scan-${id}.${format}`;
    a.click();
    URL.revokeObjectURL(a.href);
  },
};
