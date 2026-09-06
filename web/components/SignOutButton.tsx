"use client";

import { LogOut } from "lucide-react";
import { createClient } from "@/lib/supabase/client";

export function SignOutButton() {
  const handleSignOut = async () => {
    const supabase = createClient();
    await supabase.auth.signOut();
    // Full navigation: guarantees middleware sees the cleared session
    // cookie before /today would otherwise render from client cache.
    // eslint-disable-next-line @next/next/no-location-assign-relative-destination
    window.location.assign("/login");
  };

  return (
    <button
      onClick={handleSignOut}
      aria-label="Sign out"
      className="h-9 w-9 flex items-center justify-center rounded-full text-text-faint hover:text-text hover:bg-surface-2"
    >
      <LogOut size={16} />
    </button>
  );
}
