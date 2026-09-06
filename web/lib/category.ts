import {
  BatteryCharging,
  BookOpen,
  Briefcase,
  Clock3,
  Code2,
  Moon,
  Sparkles,
  UtensilsCrossed,
  type LucideIcon,
} from "lucide-react";

export interface CategoryMeta {
  icon: LucideIcon;
  colorVar: string;
}

const DEFAULT_META: CategoryMeta = { icon: Clock3, colorVar: "var(--text-muted)" };

const CATEGORY_META: Record<string, CategoryMeta> = {
  Prayer: { icon: Moon, colorVar: "var(--prayer)" },
  InterviewPrep: { icon: Code2, colorVar: "var(--accent)" },
  Job: { icon: Briefcase, colorVar: "var(--text-muted)" },
  Thesis: { icon: BookOpen, colorVar: "var(--mastery-l4)" },
  English: { icon: Sparkles, colorVar: "var(--mastery-l3)" },
  Nutrition: { icon: UtensilsCrossed, colorVar: "var(--status-partial)" },
  Recovery: { icon: BatteryCharging, colorVar: "var(--status-rescheduled)" },
  Reading: { icon: BookOpen, colorVar: "var(--mastery-l5)" },
  Buffer: { icon: Clock3, colorVar: "var(--text-faint)" },
};

export function categoryMeta(category: string): CategoryMeta {
  return CATEGORY_META[category] ?? DEFAULT_META;
}
