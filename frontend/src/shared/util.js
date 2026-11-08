export const SEVERITIES = ["Critical", "High", "Medium", "Low", "Info"];

// Class names must be written out in full so Tailwind can find them.
export const SEV = {
  Critical: { badge: "bg-[#F9DEDC] text-[#8C1A13]", border: "border-l-[#B3261E]", bar: "bg-[#B3261E]", hex: "#B3261E" },
  High: { badge: "bg-[#FBE3D6] text-[#8A3611]", border: "border-l-[#C2511F]", bar: "bg-[#C2511F]", hex: "#C2511F" },
  Medium: { badge: "bg-[#FBF1D6] text-[#6F4D00]", border: "border-l-[#D9A400]", bar: "bg-[#D9A400]", hex: "#D9A400" },
  Low: { badge: "bg-[#DDEFE6] text-[#1E5C41]", border: "border-l-[#2F7D5B]", bar: "bg-[#2F7D5B]", hex: "#2F7D5B" },
  Info: { badge: "bg-[#E4E9ED] text-[#3F4E5B]", border: "border-l-[#9AA7B2]", bar: "bg-[#9AA7B2]", hex: "#9AA7B2" },
};

// The server sends UTC times without a "Z"; add it so the browser converts to local time.
export function fmtDate(s) {
  if (!s) return "-";
  const d = new Date(/[zZ]|[+-]\d\d:?\d\d$/.test(s) ? s : s + "Z");
  return d.toLocaleString([], { dateStyle: "medium", timeStyle: "short" });
}

export const isRunning = (scan) => scan && (scan.status === "queued" || scan.status === "running");
