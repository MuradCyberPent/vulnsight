import { SEV } from "../../../shared/util";

// The one memorable element: a half-circle gauge showing the overall risk score.
export default function RiskDial({ score, level, size = 220 }) {
  const color = (SEV[level] || SEV.Low).hex;
  const arc = "M 20 100 A 80 80 0 0 1 180 100";
  return (
    <figure className="m-0 text-center" style={{ width: size }}>
      <svg viewBox="0 0 200 120" role="img" aria-label={`Risk ${level}, score ${score} out of 100`}>
        <path d={arc} pathLength="100" fill="none" stroke="#D8DEE3" strokeWidth="16" strokeLinecap="round" />
        <path
          d={arc} pathLength="100" fill="none" stroke={color} strokeWidth="16" strokeLinecap="round"
          strokeDasharray={`${Math.max(score, 1)} 100`}
          style={{ transition: "stroke-dasharray 0.8s ease" }}
        />
        <text x="100" y="92" textAnchor="middle" className="fill-ink font-display" style={{ fontSize: 44, fontWeight: 700 }}>
          {score}
        </text>
        <text x="100" y="114" textAnchor="middle" className="fill-muted" style={{ fontSize: 13 }}>
          out of 100
        </text>
      </svg>
      <figcaption className="-mt-1 font-display text-xl font-bold" style={{ color }}>{level} risk</figcaption>
    </figure>
  );
}
