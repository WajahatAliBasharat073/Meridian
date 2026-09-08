import { createServerClient, type CookieOptions } from "@supabase/ssr";
import { NextResponse, type NextRequest } from "next/server";
import { SUPABASE_ANON_KEY, SUPABASE_URL } from "@/lib/supabase/env";

// Reachable without an existing session.
const PUBLIC_PATHS = ["/login", "/forgot-password", "/reset-password", "/auth"];
// Of those, only these redirect an already-signed-in user away — not
// /reset-password (having a session there is the expected recovery-flow
// state) and not /auth (a route handler, not a page to bounce from).
const AUTH_ENTRY_PATHS = ["/login", "/forgot-password"];

export async function proxy(request: NextRequest) {
  let response = NextResponse.next({ request });

  // Every cookie @supabase/ssr asks us to write, kept so a *redirect*
  // response can carry them too. Without this, `getUser()` below rotating
  // the refresh token would write the new cookies onto `response`, and
  // then returning `NextResponse.redirect(...)` instead would silently
  // drop them — the browser keeps the old, now-invalidated refresh token,
  // the next request fails auth, and you bounce between /login and /today
  // while genuinely signed in.
  const pendingCookies: { name: string; value: string; options?: CookieOptions }[] = [];

  const supabase = createServerClient(SUPABASE_URL, SUPABASE_ANON_KEY, {
    cookies: {
      getAll() {
        return request.cookies.getAll();
      },
      setAll(cookiesToSet) {
        for (const { name, value } of cookiesToSet) request.cookies.set(name, value);
        response = NextResponse.next({ request });
        for (const { name, value, options } of cookiesToSet) {
          response.cookies.set(name, value, options);
          pendingCookies.push({ name, value, options });
        }
      },
    },
  });

  const withCookies = (res: NextResponse) => {
    for (const { name, value, options } of pendingCookies) {
      res.cookies.set(name, value, options);
    }
    return res;
  };

  // Refreshes the session if expired — required on every request per
  // @supabase/ssr's Next.js middleware pattern, not optional polish.
  const {
    data: { user },
  } = await supabase.auth.getUser();

  const { pathname } = request.nextUrl;
  const isPublicPath = PUBLIC_PATHS.some((p) => pathname.startsWith(p));
  const isAuthEntryPath = AUTH_ENTRY_PATHS.some((p) => pathname.startsWith(p));
  const isApiRoute = pathname.startsWith("/api");

  if (!user && !isPublicPath && !isApiRoute) {
    const url = request.nextUrl.clone();
    url.pathname = "/login";
    return withCookies(NextResponse.redirect(url));
  }

  if (user && isAuthEntryPath) {
    const url = request.nextUrl.clone();
    url.pathname = "/today";
    return withCookies(NextResponse.redirect(url));
  }

  return response;
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico|.*\\.(?:svg|png|jpg|jpeg|gif|webp)$).*)"],
};
