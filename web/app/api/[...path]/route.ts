/**
 * Thin server-side proxy to the FastAPI backend. Exists so the auth
 * token never reaches the browser bundle — same discipline the build
 * prompt requires for the Groq key (2.1), applied to this dev-only
 * Supabase-signed token until real Supabase Auth is wired into the
 * client (not yet built; see web/README.md).
 */
import { NextRequest, NextResponse } from "next/server";

const API_BASE_URL = process.env.API_BASE_URL ?? "http://localhost:8000";
const API_DEV_TOKEN = process.env.API_DEV_TOKEN ?? "";

async function proxy(req: NextRequest, path: string[]): Promise<NextResponse> {
  const url = new URL(`${API_BASE_URL}/api/${path.join("/")}`);
  url.search = req.nextUrl.search;

  const headers: Record<string, string> = { "Content-Type": "application/json" };
  if (API_DEV_TOKEN) headers.Authorization = `Bearer ${API_DEV_TOKEN}`;

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
