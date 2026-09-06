import { cn } from "@/lib/cn";

const WIDTH = {
  narrow: "max-w-lg",
  default: "max-w-3xl",
  wide: "max-w-5xl",
} as const;

export function PageContainer({
  children,
  width = "default",
  className,
}: {
  children: React.ReactNode;
  width?: keyof typeof WIDTH;
  className?: string;
}) {
  return (
    <main className={cn("mx-auto w-full px-4 py-6 pb-24 md:px-8 md:pb-16", WIDTH[width], className)}>
      {children}
    </main>
  );
}
