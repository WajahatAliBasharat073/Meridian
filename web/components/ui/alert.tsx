import { AlertCircle, CheckCircle2, Info } from "lucide-react";
import { cn } from "@/lib/cn";

type AlertVariant = "error" | "success" | "info";

const VARIANT_STYLE: Record<AlertVariant, { border: string; bg: string; icon: React.ElementType; iconColor: string }> = {
  error: { border: "border-danger/30", bg: "bg-danger/10", icon: AlertCircle, iconColor: "text-danger" },
  success: {
    border: "border-status-done/30",
    bg: "bg-status-done/10",
    icon: CheckCircle2,
    iconColor: "text-status-done",
  },
  info: { border: "border-info/30", bg: "bg-info/10", icon: Info, iconColor: "text-info" },
};

export function Alert({ variant, children }: { variant: AlertVariant; children: React.ReactNode }) {
  const { border, bg, icon: Icon, iconColor } = VARIANT_STYLE[variant];
  return (
    <div
      role={variant === "error" ? "alert" : "status"}
      className={cn("flex items-start gap-2 rounded-lg border px-3 py-2.5 text-sm text-text", border, bg)}
    >
      <Icon size={16} className={cn("shrink-0 mt-0.5", iconColor)} aria-hidden />
      <span>{children}</span>
    </div>
  );
}
