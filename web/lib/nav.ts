import {
  BookOpen,
  BrainCircuit,
  CalendarRange,
  Clock3,
  Code2,
  FlaskConical,
  HeartPulse,
  LayoutDashboard,
  Mic,
  Settings,
  Target,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  /** Real route, but the backing API is not shipped yet. */
  soon?: boolean;
  /** Shown in the mobile bottom bar. */
  primary?: boolean;
}

export interface NavGroup {
  label: string;
  items: NavItem[];
}

/**
 * Information architecture organized around life domains, not around
 * interview prep — Today (what to do right now) and Insights (how time
 * is actually going) are the two standalone anchors; interview prep,
 * DSA, and reading all live under Learn as one module among several,
 * not as the platform itself.
 *
 * Exists with live APIs: Today, Insights (/dashboard), Problems, ML & GenAI, Settings.
 * Exists as schema-backed routes (no API yet): Mocks, Reading, Research, Recovery.
 * Deliberately omitted (no table or API): Jobs, Applications, Courses, Goals, Tasks.
 */
export const NAV_GROUPS: NavGroup[] = [
  {
    label: "Today",
    items: [{ href: "/today", label: "Today", icon: Clock3, primary: true }],
  },
  {
    label: "Insights",
    items: [
      { href: "/dashboard", label: "Insights", icon: LayoutDashboard, primary: true },
      { href: "/goals", label: "Goals", icon: Target },
      { href: "/weekly-review", label: "Weekly Review", icon: CalendarRange },
    ],
  },
  {
    label: "Learn",
    items: [
      { href: "/problems", label: "Problems", icon: Code2, primary: true },
      { href: "/concepts", label: "ML & GenAI", icon: BrainCircuit },
      { href: "/mocks", label: "Mocks", icon: Mic, soon: true },
      { href: "/reading", label: "Reading", icon: BookOpen, soon: true },
      { href: "/research", label: "Research", icon: FlaskConical, soon: true },
    ],
  },
  {
    label: "Health",
    items: [{ href: "/health", label: "Recovery", icon: HeartPulse, soon: true }],
  },
];

export const SETTINGS_ITEM: NavItem = {
  href: "/settings",
  label: "Settings",
  icon: Settings,
};

export const ALL_NAV_ITEMS: NavItem[] = [
  ...NAV_GROUPS.flatMap((g) => g.items),
  SETTINGS_ITEM,
];

export function isNavActive(pathname: string, href: string): boolean {
  return pathname === href || pathname.startsWith(`${href}/`);
}
