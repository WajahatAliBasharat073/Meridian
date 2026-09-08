/**
 * Tiny "is my session visible to the server yet?" probe.
 *
 * The login page waits on this before navigating, because @supabase/ssr
 * writes the session cookie via document.cookie and that write races the
 * navigation (see lib/auth-handoff.ts). It deliberately touches nothing
 * but the cookie — no FastAPI call — so a backend that is down or moved
 * can never masquerade as "you are not signed in".
 *
 * More specific than app/api/[...path]/route.ts, so it wins the match.
 */
import { NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

export async function GET(): Promise<NextResponse> {
  const supabase = await createClient();
  const {
    data: { user },
    error,
  } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json(
      { authenticated: false, reason: error?.message ?? "no session" },
      { status: 401 }
    );
  }

  return NextResponse.json({ authenticated: true });
}
