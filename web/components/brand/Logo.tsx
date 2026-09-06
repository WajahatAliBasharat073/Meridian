import { cn } from "@/lib/cn";

export function LogoMark({ className, title }: { className?: string; title?: string }) {
  return (
    <svg
      viewBox="0 0 32 32"
      className={className}
      fill="none"
      role="img"
      aria-label={title ?? "Meridian"}
    >
      <path
        d="M4 24C9.5 10 22.5 10 28 24"
        stroke="var(--prayer)"
        strokeWidth="1.75"
        strokeLinecap="round"
      />
      <line
        x1="16"
        y1="3.5"
        x2="16"
        y2="28.5"
        stroke="var(--accent-strong)"
        strokeWidth="1.75"
        strokeLinecap="round"
      />
      <circle cx="16" cy="10.5" r="2.35" fill="var(--prayer)" />
    </svg>
  );
}

export function Logo({
  className,
  markClassName,
  wordmark = true,
}: {
  className?: string;
  markClassName?: string;
  wordmark?: boolean;
}) {
  return (
    <span className={cn("inline-flex items-center gap-2.5", className)}>
      <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-surface-2 border border-border shrink-0">
        <LogoMark className={cn("h-5 w-5", markClassName)} />
      </span>
      {wordmark && (
        <span className="text-[13px] font-semibold tracking-[0.18em] uppercase text-text">
          Meridian
        </span>
      )}
    </span>
  );
}
