import {
  BookOpen,
  Bot,
  BrainCircuit,
  Calendar,
  CalendarRange,
  Clock3,
  Code2,
  FlaskConical,
  GraduationCap,
  Library,
  HeartPulse,
  LayoutDashboard,
  Settings,
  Target,
  type LucideIcon,
} from "lucide-react";

export interface NavItem {
  href: string;
  label: string;
  icon: LucideIcon;
  soon?: boolean;
  primary?: boolean;
}

export interface NavGroup {
  label: string;
  items: NavItem[];
}

/**
 * Information Architecture for Meridian:
 * Life, Time & Learning Operating System.
 *
 * Core surfaces:
 * 1. Today: Command center, living activity timers, vitals, daily execution
 * 2. Plan: Architecture of time, routines, capacity, weekly time budgets
 * 3. Learn: ML & GenAI, DSA problems, research hub, reading log
 * 4. Insights: Time curve, focus analytics, planned vs actual, weekly review
 * 5. Goals: Objectives connected directly to logged activity minutes
 * 6. Coach: Ask Meridian conversational AI coach
 * 7. Health: Recovery, sleep, hydration, biological stamina
 * 8. Settings: Audio chimes, notification preferences, model keys
 */
export const NAV_GROUPS: NavGroup[] = [
  {
    label: "Today",
    items: [{ href: "/today", label: "Today", icon: Clock3, primary: true }],
  },
  {
    label: "Plan",
    items: [{ href: "/plan", label: "Plan", icon: Calendar, primary: true }],
  },
  {
    label: "Learn",
    items: [
      { href: "/curriculum", label: "Interview Curriculum", icon: GraduationCap },
      { href: "/concepts", label: "ML & GenAI", icon: BrainCircuit },
      { href: "/problems", label: "DSA Curriculum", icon: Code2 },
      { href: "/research", label: "Research & Thesis", icon: FlaskConical },
      { href: "/resources", label: "Learning Resources", icon: Library },
      { href: "/reading", label: "Reading Log", icon: BookOpen },
    ],
  },
  {
    label: "Insights",
    items: [
      { href: "/dashboard", label: "Insights Hub", icon: LayoutDashboard, primary: true },
      { href: "/weekly-review", label: "Weekly Review", icon: CalendarRange },
    ],
  },
  {
    label: "Goals",
    items: [{ href: "/goals", label: "Goals", icon: Target }],
  },
  {
    label: "Coach",
    items: [{ href: "/coach", label: "Ask Meridian", icon: Bot, primary: true }],
  },
  {
    label: "Health",
    items: [{ href: "/health", label: "Recovery", icon: HeartPulse }],
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
