import { useEffect, useState } from "react";
import { createClient } from "@/lib/supabase/client";

/** Cheap client-side read of the already-authenticated session — no
 * extra network round trip to our own API, just what the browser's
 * Supabase client already holds. */
export function useCurrentUser() {
  const [email, setEmail] = useState<string | null>(null);

  useEffect(() => {
    const supabase = createClient();
    supabase.auth.getUser().then(({ data }) => setEmail(data.user?.email ?? null));
  }, []);

  return { email };
}
