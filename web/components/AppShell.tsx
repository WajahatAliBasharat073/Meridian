"use client";

import { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Menu, X } from "lucide-react";
import { Logo, LogoMark } from "@/components/brand/Logo";
import { SidebarNav } from "@/components/layout/Sidebar";
import { TopNav } from "@/components/layout/TopNav";
import { SignOutButton } from "@/components/SignOutButton";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { cn } from "@/lib/cn";
import { ALL_NAV_ITEMS, isNavActive } from "@/lib/nav";

import { NotificationCenter } from "@/components/ui/NotificationCenter";

export function AppShell({ children }: { children: React.ReactNode }) {
  const [drawerOpen, setDrawerOpen] = useState(false);
  const pathname = usePathname();
  const { email } = useCurrentUser();
  const primary = ALL_NAV_ITEMS.filter((item) => item.primary);

  return (
    <div className="min-h-screen">
      <NotificationCenter />
      <TopNav />

      <div className="md:hidden sticky top-0 z-20 border-b border-border bg-surface/95 backdrop-blur flex items-center justify-between h-14 px-3">
        <button
          onClick={() => setDrawerOpen(true)}
          aria-label="Open navigation"
          className="h-11 w-11 flex items-center justify-center rounded-lg text-text-muted hover:text-text hover:bg-surface-2"
        >
          <Menu size={20} />
        </button>
        <Link href="/today" className="inline-flex items-center gap-2">
          <LogoMark className="h-5 w-5" />
          <span className="text-[13px] font-semibold tracking-[0.16em] uppercase text-text">
            Meridian
          </span>
        </Link>
        <SignOutButton />
      </div>

      {drawerOpen && (
        <div className="md:hidden fixed inset-0 z-30">
          <button
            type="button"
            className="absolute inset-0 bg-black/60"
            onClick={() => setDrawerOpen(false)}
            aria-label="Close navigation"
          />
          <div className="absolute left-0 top-0 h-full w-72 max-w-[85vw] bg-surface border-r border-border flex flex-col">
            <div className="flex items-center justify-between px-4 py-4">
              <Logo />
              <button
                onClick={() => setDrawerOpen(false)}
                aria-label="Close navigation"
                className="h-11 w-11 flex items-center justify-center rounded-lg text-text-muted hover:text-text"
              >
                <X size={20} />
              </button>
            </div>
            <div className="flex-1 min-h-0">
              <SidebarNav showBrand={false} onNavigate={() => setDrawerOpen(false)} />
            </div>
            <div className="px-3 pb-4 border-t border-border pt-3">
              {email && (
                <p className="px-3 mb-2 text-xs text-text-faint truncate">{email}</p>
              )}
              <SignOutButton labeled />
            </div>
          </div>
        </div>
      )}

      <div>{children}</div>

      <nav
        className="md:hidden fixed bottom-0 inset-x-0 z-20 border-t border-border bg-surface/95 backdrop-blur pb-[env(safe-area-inset-bottom)]"
        aria-label="Primary"
      >
        <div className="grid grid-cols-3 h-14">
          {primary.map((item) => {
            const Icon = item.icon;
            const active = isNavActive(pathname, item.href);
            return (
              <Link
                key={item.href}
                href={item.href}
                aria-current={active ? "page" : undefined}
                className={cn(
                  "flex flex-col items-center justify-center gap-0.5 text-[11px] font-medium",
                  active ? "text-accent-strong" : "text-text-faint"
                )}
              >
                <Icon size={18} />
                {item.label}
              </Link>
            );
          })}
        </div>
      </nav>
    </div>
  );
}
