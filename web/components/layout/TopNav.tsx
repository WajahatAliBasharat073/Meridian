"use client";

import { useEffect, useRef, useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { ChevronDown } from "lucide-react";
import { Logo } from "@/components/brand/Logo";
import { LifeClockPill } from "@/components/layout/LifeClockPill";
import { NotificationBellButton } from "@/components/ui/NotificationCenter";
import { cn } from "@/lib/cn";
import { isNavActive, NAV_GROUPS, SETTINGS_ITEM, type NavGroup, type NavItem } from "@/lib/nav";

function DropdownItem({
  item,
  pathname,
  onNavigate,
}: {
  item: NavItem;
  pathname: string;
  onNavigate: () => void;
}) {
  const active = isNavActive(pathname, item.href);
  const Icon = item.icon;

  return (
    <Link
      href={item.href}
      onClick={onNavigate}
      aria-current={active ? "page" : undefined}
      className={cn(
        "h-10 px-3 rounded-lg text-sm font-medium flex items-center gap-2.5 transition-colors",
        active ? "bg-accent-soft text-accent-strong" : "text-text-muted hover:text-text hover:bg-surface-2"
      )}
    >
      <Icon size={15} className="shrink-0" />
      <span className="flex-1">{item.label}</span>
      {item.soon && (
        <span className="text-[9px] font-medium uppercase tracking-wide text-text-faint border border-border rounded-full px-1.5 py-0.5 shrink-0">
          Soon
        </span>
      )}
    </Link>
  );
}

function SoloNavLink({ item, pathname }: { item: NavItem; pathname: string }) {
  const active = isNavActive(pathname, item.href);
  const Icon = item.icon;

  return (
    <Link
      href={item.href}
      aria-current={active ? "page" : undefined}
      className={cn(
        "h-9 px-3 rounded-lg text-sm font-medium flex items-center gap-1.5 whitespace-nowrap transition-colors",
        active ? "bg-accent-soft text-accent-strong" : "text-text-muted hover:text-text hover:bg-surface-2"
      )}
    >
      <Icon size={15} className="shrink-0" />
      {item.label}
    </Link>
  );
}

function NavGroupMenu({
  group,
  pathname,
  openGroup,
  setOpenGroup,
}: {
  group: NavGroup;
  pathname: string;
  openGroup: string | null;
  setOpenGroup: (label: string | null) => void;
}) {
  const open = openGroup === group.label;
  const active = group.items.some((item) => isNavActive(pathname, item.href));

  // A single-item group (Today, Insights) is just a direct link — no
  // dropdown chevron for something with nothing to expand into.
  if (group.items.length === 1) {
    return <SoloNavLink item={group.items[0]} pathname={pathname} />;
  }

  return (
    <div
      className="relative"
      onMouseEnter={() => setOpenGroup(group.label)}
      onMouseLeave={() => setOpenGroup(null)}
    >
      <button
        type="button"
        onClick={() => setOpenGroup(open ? null : group.label)}
        aria-expanded={open}
        className={cn(
          "h-9 px-3 rounded-lg text-sm font-medium flex items-center gap-1.5 whitespace-nowrap transition-colors",
          active || open
            ? "bg-accent-soft text-accent-strong"
            : "text-text-muted hover:text-text hover:bg-surface-2"
        )}
      >
        {group.label}
        <ChevronDown size={13} className={cn("transition-transform", open && "rotate-180")} />
      </button>

      {open && (
        <div className="absolute left-0 top-full pt-1.5 z-30">
          <div className="w-56 rounded-xl border border-border bg-surface shadow-elevated p-1.5">
            {group.items.map((item) => (
              <DropdownItem
                key={item.href}
                item={item}
                pathname={pathname}
                onNavigate={() => setOpenGroup(null)}
              />
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

export function TopNav() {
  const pathname = usePathname();
  const SettingsIcon = SETTINGS_ITEM.icon;
  const [openGroup, setOpenGroup] = useState<string | null>(null);
  const navRef = useRef<HTMLElement>(null);

  useEffect(() => {
    if (!openGroup) return;
    const onKeyDown = (e: KeyboardEvent) => {
      if (e.key === "Escape") setOpenGroup(null);
    };
    const onClickOutside = (e: MouseEvent) => {
      if (navRef.current && !navRef.current.contains(e.target as Node)) setOpenGroup(null);
    };
    document.addEventListener("keydown", onKeyDown);
    document.addEventListener("mousedown", onClickOutside);
    return () => {
      document.removeEventListener("keydown", onKeyDown);
      document.removeEventListener("mousedown", onClickOutside);
    };
  }, [openGroup]);

  return (
    <header className="hidden md:grid sticky top-0 z-20 h-16 grid-cols-[auto_1fr_auto] items-center border-b border-border bg-surface/95 backdrop-blur px-4 lg:px-6">
      <Link href="/today" className="inline-flex shrink-0">
        <Logo />
      </Link>

      <nav ref={navRef} className="flex items-center justify-center gap-1" aria-label="Main">
        {NAV_GROUPS.map((group) => (
          <NavGroupMenu
            key={group.label}
            group={group}
            pathname={pathname}
            openGroup={openGroup}
            setOpenGroup={setOpenGroup}
          />
        ))}
      </nav>

      <div className="flex items-center justify-end gap-1 shrink-0">
        <LifeClockPill />
        <NotificationBellButton />
        <Link
          href={SETTINGS_ITEM.href}
          aria-current={isNavActive(pathname, SETTINGS_ITEM.href) ? "page" : undefined}
          aria-label={SETTINGS_ITEM.label}
          className={cn(
            "h-9 w-9 rounded-lg flex items-center justify-center transition-colors",
            isNavActive(pathname, SETTINGS_ITEM.href)
              ? "bg-accent-soft text-accent-strong"
              : "text-text-muted hover:text-text hover:bg-surface-2"
          )}
        >
          <SettingsIcon size={16} />
        </Link>
      </div>
    </header>
  );
}
