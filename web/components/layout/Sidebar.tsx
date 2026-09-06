"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  BookOpen,
  Clock3,
  Code2,
  FlaskConical,
  HeartPulse,
  LayoutDashboard,
  Mic,
  Settings,
  type LucideIcon,
} from "lucide-react";
import { cn } from "@/lib/cn";

interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  soon?: boolean;
}

interface NavGroup {
  label?: string;
  items: NavItem[];
}

/** The full product surface, and nothing else — every entry here maps to
 * a real database table. Career-style sections (Jobs, Applications,
 * Goals) deliberately don't appear: nothing in the schema backs them, and
 * inventing nav for data that can't exist yet is exactly the "fake
 * functionality" this product refuses to ship. */
const NAV_GROUPS: NavGroup[] = [
  {
    items: [
      { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
      { href: "/today", label: "Today", icon: Clock3 },
    ],
  },
  {
    label: "Interview Prep",
    items: [
      { href: "/problems", label: "Problems", icon: Code2 },
      { href: "/mocks", label: "Mocks", icon: Mic, soon: true },
    ],
  },
  {
    label: "Learning",
    items: [
      { href: "/reading", label: "Reading", icon: BookOpen, soon: true },
      { href: "/research", label: "Research", icon: FlaskConical, soon: true },
    ],
  },
  {
    label: "Health",
    items: [{ href: "/health", label: "Recovery & Nutrition", icon: HeartPulse, soon: true }],
  },
];

export function SidebarNav({ onNavigate }: { onNavigate?: () => void }) {
  const pathname = usePathname();

  return (
    <nav className="flex flex-col h-full">
      <div className="px-4 py-5">
        <span className="text-sm font-semibold uppercase tracking-[0.15em] text-accent">
          Meridian
        </span>
      </div>

      <div className="flex-1 overflow-y-auto px-3 space-y-5">
        {NAV_GROUPS.map((group, i) => (
          <div key={group.label ?? i}>
            {group.label && (
              <p className="px-3 mb-1.5 text-[11px] font-medium uppercase tracking-wide text-text-faint">
                {group.label}
              </p>
            )}
            <div className="space-y-0.5">
              {group.items.map((item) => {
                const active = pathname === item.href;
                const Icon = item.icon;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    onClick={onNavigate}
                    aria-current={active ? "page" : undefined}
                    className={cn(
                      "h-11 px-3 rounded-md text-sm font-medium flex items-center gap-2.5 transition-colors",
                      active
                        ? "bg-accent-soft text-accent-strong"
                        : "text-text-muted hover:text-text hover:bg-surface-2"
                    )}
                  >
                    <Icon size={16} className="shrink-0" />
                    <span className="truncate">{item.label}</span>
                    {item.soon && (
                      <span className="ml-auto text-[10px] text-text-faint border border-border rounded px-1.5 py-0.5 shrink-0">
                        Soon
                      </span>
                    )}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      <div className="px-3 py-3 border-t border-border">
        <Link
          href="/settings"
          onClick={onNavigate}
          aria-current={pathname === "/settings" ? "page" : undefined}
          className={cn(
            "h-11 px-3 rounded-md text-sm font-medium flex items-center gap-2.5 transition-colors",
            pathname === "/settings"
              ? "bg-accent-soft text-accent-strong"
              : "text-text-muted hover:text-text hover:bg-surface-2"
          )}
        >
          <Settings size={16} />
          Settings
        </Link>
      </div>
    </nav>
  );
}
