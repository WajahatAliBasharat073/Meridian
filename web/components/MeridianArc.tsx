/** Decorative brand mark: the sun's arc across the sky, the same
 * geometry that drives every prayer time (and therefore the whole
 * schedule) in the actual product — not a generic gradient blob. */
export function MeridianArc({ className }: { className?: string }) {
  return (
    <svg
      viewBox="0 0 460 260"
      className={className}
      fill="none"
      role="img"
      aria-label="Illustration of the sun's arc across the sky, marking Fajr, Zuhr, Asr, Maghrib and Isha"
    >
      <defs>
        <radialGradient id="sunGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="var(--prayer)" stopOpacity="0.55" />
          <stop offset="100%" stopColor="var(--prayer)" stopOpacity="0" />
        </radialGradient>
        <linearGradient id="arcFade" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0%" stopColor="var(--prayer)" stopOpacity="0.35" />
          <stop offset="50%" stopColor="var(--prayer)" stopOpacity="0.9" />
          <stop offset="100%" stopColor="var(--prayer)" stopOpacity="0.35" />
        </linearGradient>
      </defs>

      {/* below-horizon continuation (Fajr before sunrise, Isha after sunset) */}
      <path
        d="M 8 236 Q 40 205 40 205 M 420 205 Q 452 236 452 236"
        stroke="var(--border-strong)"
        strokeWidth="1.5"
        strokeDasharray="2 5"
        strokeLinecap="round"
      />

      {/* horizon */}
      <line x1="8" y1="205" x2="452" y2="205" stroke="var(--border-strong)" strokeWidth="1.5" />

      {/* the day arc */}
      <path d="M 40 205 Q 230 20 420 205" stroke="url(#arcFade)" strokeWidth="2" strokeLinecap="round" />

      {/* sun, at the arc's peak (Zuhr) */}
      <circle cx="230" cy="112" r="46" fill="url(#sunGlow)" />
      <circle cx="230" cy="112" r="9" fill="var(--prayer)" />

      {/* prayer ticks along the arc */}
      {[
        { x: 8, y: 236, label: "FAJR" },
        { x: 40, y: 205, label: "SUNRISE" },
        { x: 230, y: 20, label: "ZUHR" },
        { x: 325, y: 136, label: "ASR" },
        { x: 420, y: 205, label: "MAGHRIB" },
        { x: 452, y: 236, label: "ISHA" },
      ].map((p) => (
        <circle key={p.label} cx={p.x} cy={p.y} r="3" fill="var(--text-faint)" />
      ))}

      <g
        className="tabular-nums"
        style={{ font: "500 10px var(--font-mono)", letterSpacing: "0.06em", fill: "var(--text-faint)" }}
      >
        <text x="8" y="256" textAnchor="start">FAJR</text>
        <text x="230" y="14" textAnchor="middle">ZUHR</text>
        <text x="341" y="120" textAnchor="start">ASR</text>
        <text x="420" y="228" textAnchor="middle">MAGHRIB</text>
      </g>
    </svg>
  );
}
