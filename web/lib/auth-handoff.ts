/** Bridges the gap between "Supabase says you're signed in" and "the
 * server can see it".
 *
 * `@supabase/ssr`'s browser client persists the session by writing
 * `document.cookie`. That write is not synchronous with the promise from
 * `signInWithPassword()` resolving, so navigating immediately after
 * sign-in races it: the browser can issue the request for the next page
 * (or begin unloading, dropping the write entirely) before the cookie is
 * in the jar. The middleware then sees no session and bounces straight
 * back to /login — a sign-in that succeeded, looking exactly like a
 * failed one.
 *
 * So: wait for the cookie to actually exist, then confirm the *server*
 * can read it, and only then hand off. */

const COOKIE_PREFIX = "sb-";
const AUTH_COOKIE_MARKER = "-auth-token";

function hasAuthCookie(): boolean {
  return document.cookie
    .split(";")
    .some((c) => {
      const name = c.split("=")[0]?.trim() ?? "";
      return name.startsWith(COOKIE_PREFIX) && name.includes(AUTH_COOKIE_MARKER);
    });
}

/** Resolves once the server accepts our session, or false on timeout. */
export async function waitForServerSession(timeoutMs = 5000): Promise<boolean> {
  const deadline = Date.now() + timeoutMs;

  // 1. The cookie has to be in the jar before any request will carry it.
  while (Date.now() < deadline) {
    if (hasAuthCookie()) break;
    await new Promise((r) => setTimeout(r, 50));
  }
  if (!hasAuthCookie()) return false;

  // 2. Confirm the *server* actually reads it, via a probe that checks
  //    only the cookie — never the FastAPI backend, so a backend that is
  //    down or moved can't be mistaken for "not signed in".
  while (Date.now() < deadline) {
    try {
      const res = await fetch("/api/auth/session-check", { cache: "no-store" });
      if (res.ok) return true;
    } catch {
      // network hiccup — fall through and retry until the deadline
    }
    await new Promise((r) => setTimeout(r, 100));
  }

  return false;
}
