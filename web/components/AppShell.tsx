"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/cn";
import { SignOutButton } from "@/components/SignOutButton";

const NAV_ITEMS = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/today", label: "Today" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <>
      <nav className="sticky top-0 z-10 border-b border-border bg-surface/95 backdrop-blur">
        <div className="mx-auto max-w-5xl px-4 h-14 flex items-center justify-between">
          <div className="flex items-center gap-1">
            <span className="text-sm font-semibold uppercase tracking-[0.15em] text-accent mr-4">
              Meridian
            </span>
            {NAV_ITEMS.map((item) => {
              const active = pathname === item.href;
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  aria-current={active ? "page" : undefined}
                  className={cn(
                    "h-9 px-3 rounded-md text-sm font-medium flex items-center transition-colors",
                    active
                      ? "bg-accent-soft text-accent-strong"
                      : "text-text-muted hover:text-text hover:bg-surface-2"
                  )}
                >
                  {item.label}
                </Link>
              );
            })}
          </div>
          <SignOutButton />
        </div>
      </nav>
      {children}
    </>
  );
}
