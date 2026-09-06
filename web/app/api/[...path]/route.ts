/**
 * Server-side proxy to the FastAPI backend. Reads the caller's real
 * Supabase session (cookies, refreshed by proxy.ts) and forwards
 * their access token — the token itself never reaches client JS, only
 * the httpOnly session cookie does, same discipline the build prompt
 * requires for the Groq key (2.1).
 */
import { NextRequest, NextResponse } from "next/server";
import { createClient } from "@/lib/supabase/server";

const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000";

async function proxy(req: NextRequest, path: string[]): Promise<NextResponse> {
  const supabase = await createClient();
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    return NextResponse.json({ detail: "Not authenticated" }, { status: 401 });
  }

  const {
    data: { session },
  } = await supabase.auth.getSession();

  const url = new URL(`${API_BASE_URL}/api/${path.join("/")}`);
  url.search = req.nextUrl.search;

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    Authorization: `Bearer ${session?.access_token}`,
  };

  const init: RequestInit = { method: req.method, headers };
  if (req.method !== "GET" && req.method !== "HEAD") {
    init.body = await req.text();
  }

  const upstream = await fetch(url, init);
  const body = await upstream.text();
  return new NextResponse(body, {
    status: upstream.status,
    headers: { "Content-Type": upstream.headers.get("content-type") ?? "application/json" },
  });
}

type RouteParams = { params: Promise<{ path: string[] }> };

export async function GET(req: NextRequest, ctx: RouteParams): Promise<NextResponse> {
  return proxy(req, (await ctx.params).path);
}

export async function POST(req: NextRequest, ctx: RouteParams): Promise<NextResponse> {
  return proxy(req, (await ctx.params).path);
}
