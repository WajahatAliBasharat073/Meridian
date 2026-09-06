"use client";

import { LogOut } from "lucide-react";
import { createClient } from "@/lib/supabase/client";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/cn";

export function SignOutButton({
  labeled = false,
  className,
}: {
  labeled?: boolean;
  className?: string;
}) {
  const handleSignOut = async () => {
    const supabase = createClient();
    await supabase.auth.signOut();
    // Full navigation: guarantees middleware sees the cleared session
    // cookie before /today would otherwise render from client cache.
    // eslint-disable-next-line @next/next/no-location-assign-relative-destination
    window.location.assign("/login");
  };

  if (labeled) {
    return (
      <Button
        variant="ghost"
        size="sm"
        onClick={handleSignOut}
        className={cn("w-full justify-start", className)}
      >
        <LogOut size={16} />
        Sign out
      </Button>
    );
  }

  return (
    <button
      onClick={handleSignOut}
      aria-label="Sign out"
      className={cn(
        "h-11 w-11 flex items-center justify-center rounded-lg text-text-faint hover:text-text hover:bg-surface-2",
        className
      )}
    >
      <LogOut size={16} />
    </button>
  );
}
