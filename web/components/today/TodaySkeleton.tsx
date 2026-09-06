import { Skeleton } from "@/components/ui/skeleton";

export function TodaySkeleton() {
  return (
    <div className="space-y-4">
      <Skeleton className="h-[180px] w-full" />
      <Skeleton className="h-16 w-full" />
      <Skeleton className="h-[220px] w-full" />
      <Skeleton className="h-24 w-full" />
      <Skeleton className="h-[400px] w-full" />
    </div>
  );
}
