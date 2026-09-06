"use client";

import Link from "next/link";
import { useState } from "react";
import { Eye, EyeOff, Loader2, Lock, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { FieldLabel } from "@/components/ui/field-label";
import { Alert } from "@/components/ui/alert";
import { MeridianArc } from "@/components/MeridianArc";
import { createClient } from "@/lib/supabase/client";

type Mode = "signin" | "signup";

export default function LoginPage() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [mode, setMode] = useState<Mode>("signin");
  const [error, setError] = useState<string | null>(null);
  const [notice, setNotice] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setNotice(null);
    setLoading(true);

    const supabase = createClient();
    const { data, error: authError } =
      mode === "signin"
        ? await supabase.auth.signInWithPassword({ email, password })
        : await supabase.auth.signUp({ email, password });

    if (authError) {
      setLoading(false);
      setError(authError.message);
      return;
    }

    if (mode === "signup" && !data.session) {
      setLoading(false);
      setNotice("Account created — check your email to confirm it, then sign in.");
      setMode("signin");
      return;
    }

    // Full navigation, not router.push: guarantees the server sees the
    // fresh session cookie on the very next request (proxy.ts). Stay in
    // the loading state until the browser actually leaves this page.
    // eslint-disable-next-line @next/next/no-location-assign-relative-destination
    window.location.assign("/today");
  };

  const switchMode = (next: Mode) => {
    setMode(next);
    setError(null);
    setNotice(null);
  };

  return (
    <main className="min-h-screen lg:grid lg:grid-cols-2">
      {/* Brand panel */}
      <div className="relative hidden lg:flex flex-col justify-between overflow-hidden bg-surface border-r border-border px-12 py-12">
        <p className="text-sm font-medium uppercase tracking-[0.2em] text-accent">Meridian</p>

        <div className="flex-1 flex items-center justify-center py-8">
          <MeridianArc className="w-full max-w-md" />
        </div>

        <div className="max-w-sm">
          <h2 className="text-2xl font-semibold text-text text-balance leading-snug">
            What do I do right now?
          </h2>
          <p className="text-sm text-text-muted mt-2 leading-relaxed">
            The solar meridian — the sun&apos;s daily crossing of your local
            north-south line — anchors every prayer time, and every prayer
            time anchors the schedule.
          </p>
        </div>
      </div>

      {/* Form panel */}
      <div className="flex items-center justify-center px-4 py-12 min-h-screen lg:min-h-0">
        <div className="w-full max-w-sm">
          <div className="lg:hidden mb-8 flex flex-col items-center text-center">
            <MeridianArc className="w-full max-w-[220px] mb-4" />
            <p className="text-sm font-medium uppercase tracking-[0.2em] text-accent">Meridian</p>
          </div>

          <h1 className="text-xl font-semibold text-text mb-1">
            {mode === "signin" ? "Welcome back" : "Create your account"}
          </h1>
          <p className="text-sm text-text-muted mb-6">
            {mode === "signin"
              ? "Sign in to see what's next."
              : "One account — this is a single-user operating system."}
          </p>

          <form onSubmit={handleSubmit} className="space-y-4" noValidate>
            <div>
              <FieldLabel htmlFor="email">Email</FieldLabel>
              <Input
                id="email"
                type="email"
                required
                autoComplete="email"
                autoFocus
                icon={<Mail size={16} />}
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="you@example.com"
              />
            </div>

            <div>
              <FieldLabel htmlFor="password" hint={mode === "signup" ? "6+ characters" : undefined}>
                Password
              </FieldLabel>
              <Input
                id="password"
                type={showPassword ? "text" : "password"}
                required
                minLength={6}
                autoComplete={mode === "signin" ? "current-password" : "new-password"}
                icon={<Lock size={16} />}
                trailing={
                  <button
                    type="button"
                    onClick={() => setShowPassword((s) => !s)}
                    aria-label={showPassword ? "Hide password" : "Show password"}
                    className="h-8 w-8 flex items-center justify-center rounded-md text-text-faint hover:text-text hover:bg-surface-hover"
                  >
                    {showPassword ? <EyeOff size={16} /> : <Eye size={16} />}
                  </button>
                }
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                placeholder="••••••••"
              />
              {mode === "signin" && (
                <Link
                  href="/forgot-password"
                  className="text-xs text-text-faint hover:text-text-muted mt-1.5 inline-block"
                >
                  Forgot password?
                </Link>
              )}
            </div>

            <div aria-live="polite" className="space-y-3">
              {error && <Alert variant="error">{error}</Alert>}
              {notice && <Alert variant="success">{notice}</Alert>}
            </div>

            <Button type="submit" variant="primary" size="lg" disabled={loading} className="w-full">
              {loading ? (
                <>
                  <Loader2 size={16} className="animate-spin" />
                  {mode === "signin" ? "Signing in…" : "Creating account…"}
                </>
              ) : mode === "signin" ? (
                "Sign in"
              ) : (
                "Create account"
              )}
            </Button>
          </form>

          <button
            onClick={() => switchMode(mode === "signin" ? "signup" : "signin")}
            className="text-sm text-text-muted hover:text-text mt-6 w-full text-center transition-colors"
          >
            {mode === "signin" ? (
              <>
                New here? <span className="text-accent-strong">Create an account</span>
              </>
            ) : (
              <>
                Already have an account? <span className="text-accent-strong">Sign in</span>
              </>
            )}
          </button>
        </div>
      </div>
    </main>
  );
}
