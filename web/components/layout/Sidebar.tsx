"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Logo } from "@/components/brand/Logo";
import { cn } from "@/lib/cn";
import { isNavActive, NAV_GROUPS, SETTINGS_ITEM, type NavItem } from "@/lib/nav";

function NavLink({
  item,
  pathname,
  onNavigate,
}: {
  item: NavItem;
  pathname: string;
  onNavigate?: () => void;
}) {
  const active = isNavActive(pathname, item.href);
  const Icon = item.icon;

  return (
    <Link
      href={item.href}
      onClick={onNavigate}
      aria-current={active ? "page" : undefined}
      className={cn(
        "group relative h-10 px-3 rounded-lg text-sm font-medium flex items-center gap-2.5 transition-colors",
        active
          ? "bg-accent-soft text-accent-strong"
          : "text-text-muted hover:text-text hover:bg-surface-2"
      )}
    >
      {active && (
        <span
          className="absolute left-0 top-1.5 bottom-1.5 w-0.5 rounded-full bg-accent"
          aria-hidden
        />
      )}
      <Icon size={16} className="shrink-0" />
      <span className="truncate">{item.label}</span>
      {item.soon && (
        <span className="ml-auto text-[10px] font-medium uppercase tracking-wide text-text-faint border border-border rounded-full px-1.5 py-0.5 shrink-0">
          Soon
        </span>
      )}
    </Link>
  );
}

export function SidebarNav({
  onNavigate,
  showBrand = true,
}: {
  onNavigate?: () => void;
  showBrand?: boolean;
}) {
  const pathname = usePathname();
  const SettingsIcon = SETTINGS_ITEM.icon;

  return (
    <nav className="flex flex-col h-full" aria-label="Main">
      {showBrand && (
        <div className="px-4 py-5">
          <Link href="/today" onClick={onNavigate} className="inline-flex">
            <Logo />
          </Link>
        </div>
      )}

      <div className={cn("flex-1 overflow-y-auto px-3 space-y-6", !showBrand && "pt-1")}>
        {NAV_GROUPS.map((group) => (
          <div key={group.label}>
            <p className="px-3 mb-1.5 text-[11px] font-medium uppercase tracking-wide text-text-faint">
              {group.label}
            </p>
            <div className="space-y-0.5">
              {group.items.map((item) => (
                <NavLink
                  key={item.href}
                  item={item}
                  pathname={pathname}
                  onNavigate={onNavigate}
                />
              ))}
            </div>
          </div>
        ))}
      </div>

      <div className="px-3 py-3 border-t border-border">
        <Link
          href={SETTINGS_ITEM.href}
          onClick={onNavigate}
          aria-current={isNavActive(pathname, SETTINGS_ITEM.href) ? "page" : undefined}
          className={cn(
            "h-10 px-3 rounded-lg text-sm font-medium flex items-center gap-2.5 transition-colors",
            isNavActive(pathname, SETTINGS_ITEM.href)
              ? "bg-accent-soft text-accent-strong"
              : "text-text-muted hover:text-text hover:bg-surface-2"
          )}
        >
          <SettingsIcon size={16} />
          {SETTINGS_ITEM.label}
        </Link>
      </div>
    </nav>
  );
}
