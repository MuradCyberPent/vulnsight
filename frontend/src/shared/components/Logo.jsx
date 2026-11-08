export default function Logo({ light = false }) {
  return (
    <span className="inline-flex items-center gap-2 font-display text-xl font-bold">
      <svg width="26" height="26" viewBox="0 0 32 32" aria-hidden="true">
        <rect width="32" height="32" rx="7" fill={light ? "#2BB3BF" : "#12263A"} />
        <circle cx="16" cy="16" r="7" fill="none" stroke={light ? "#12263A" : "#2BB3BF"} strokeWidth="3" />
        <circle cx="16" cy="16" r="2.5" fill={light ? "#12263A" : "#2BB3BF"} />
      </svg>
      VulnSight
    </span>
  );
}
