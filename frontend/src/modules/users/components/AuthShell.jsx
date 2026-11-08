import Logo from "../../../shared/components/Logo";
import SeverityBadge from "../../../shared/components/SeverityBadge";

const SAMPLE = [
  ["Critical", "Environment file (.env) is public"],
  ["High", "Redis is open to the internet"],
  ["Medium", "Missing Content-Security-Policy (CSP)"],
  ["Low", "Cookie missing the HttpOnly flag"],
];

export default function AuthShell({ title, subtitle, children, footer }) {
  return (
    <div className="grid min-h-screen md:grid-cols-2">
      <section className="hidden flex-col justify-between bg-ink p-10 text-white md:flex">
        <Logo light />
        <div>
          <h1 className="max-w-md text-4xl font-bold leading-tight">See your site the way an attacker would see it first.</h1>
          <p className="mt-4 max-w-md text-white/70">
            Scan your own servers and websites, learn what each finding means in plain English, and track your fixes over time.
          </p>
          <ul className="mt-8 max-w-md space-y-2" aria-label="Example findings">
            {SAMPLE.map(([sev, text]) => (
              <li key={text} className="flex items-center gap-3 bg-white/10 px-3 py-2 text-sm">
                <SeverityBadge level={sev} className="w-16 shrink-0 text-center" />
                {text}
              </li>
            ))}
          </ul>
        </div>
        <p className="text-sm text-white/50">Only scan systems you own or have permission to test.</p>
      </section>

      <section className="flex items-center justify-center px-6 py-12">
        <div className="w-full max-w-sm">
          <div className="mb-8 md:hidden"><Logo /></div>
          <h2 className="text-2xl font-bold">{title}</h2>
          <p className="mb-6 mt-1 text-sm text-muted">{subtitle}</p>
          {children}
          <p className="mt-6 text-sm text-muted">{footer}</p>
        </div>
      </section>
    </div>
  );
}
