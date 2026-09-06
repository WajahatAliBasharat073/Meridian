"use client";

import { useState } from "react";
import { Menu, X } from "lucide-react";
import { SidebarNav } from "@/components/layout/Sidebar";
import { SignOutButton } from "@/components/SignOutButton";

export function AppShell({ children }: { children: React.ReactNode }) {
  const [drawerOpen, setDrawerOpen] = useState(false);

  return (
    <div className="min-h-screen md:flex">
      {/* Desktop sidebar */}
      <aside className="hidden md:flex md:w-60 md:flex-col md:shrink-0 border-r border-border bg-surface md:sticky md:top-0 md:h-screen">
        <SidebarNav />
      </aside>

      {/* Mobile top bar */}
      <div className="md:hidden sticky top-0 z-20 border-b border-border bg-surface/95 backdrop-blur flex items-center justify-between h-14 px-4">
        <button
          onClick={() => setDrawerOpen(true)}
          aria-label="Open navigation"
          className="h-11 w-11 -ml-2 flex items-center justify-center text-text-muted hover:text-text"
        >
          <Menu size={20} />
        </button>
        <span className="text-sm font-semibold uppercase tracking-[0.15em] text-accent">
          Meridian
        </span>
        <SignOutButton />
      </div>

      {/* Mobile drawer */}
      {drawerOpen && (
        <div className="md:hidden fixed inset-0 z-30">
          <div
            className="absolute inset-0 bg-black/60"
            onClick={() => setDrawerOpen(false)}
            aria-hidden
          />
          <div className="absolute left-0 top-0 h-full w-72 max-w-[80vw] bg-surface border-r border-border">
            <div className="flex justify-end px-3 pt-3">
              <button
                onClick={() => setDrawerOpen(false)}
                aria-label="Close navigation"
                className="h-11 w-11 flex items-center justify-center text-text-muted hover:text-text"
              >
                <X size={20} />
              </button>
            </div>
            <SidebarNav onNavigate={() => setDrawerOpen(false)} />
          </div>
        </div>
      )}

      {/* Desktop top bar (sign-out) + page content */}
      <div className="flex-1 min-w-0">
        <div className="hidden md:flex justify-end px-6 h-14 items-center border-b border-border">
          <SignOutButton />
        </div>
        {children}
      </div>
    </div>
  );
}
