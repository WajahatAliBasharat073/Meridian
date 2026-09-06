"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { Eye, EyeOff, Loader2, Lock } from "lucide-react";
import { Logo } from "@/components/brand/Logo";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { FieldLabel } from "@/components/ui/field-label";
import { Alert } from "@/components/ui/alert";
import { createClient } from "@/lib/supabase/client";

export default function ResetPasswordPage() {
  const [checking, setChecking] = useState(true);
  const [validSession, setValidSession] = useState(false);
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const supabase = createClient();
    supabase.auth.getUser().then(({ data: { user } }) => {
      setValidSession(!!user);
      setChecking(false);
    });
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const supabase = createClient();
    const { error: authError } = await supabase.auth.updateUser({ password });

    if (authError) {
      setLoading(false);
      setError(authError.message);
      return;
    }

    // eslint-disable-next-line @next/next/no-location-assign-relative-destination
    window.location.assign("/today");
  };

  return (
    <main className="min-h-screen flex items-center justify-center px-4">
      <Card className="w-full max-w-sm p-6">
        <Logo className="mb-6" />
        <h1 className="text-xl font-semibold text-text mb-1">Set a new password</h1>

        {checking && <p className="text-sm text-text-muted mt-4">Checking your reset link…</p>}

        {!checking && !validSession && (
          <div className="mt-4 space-y-4">
            <Alert variant="error">This reset link is invalid or has expired.</Alert>
            <Link href="/forgot-password">
              <Button variant="secondary" size="md" className="w-full">
                Request a new link
              </Button>
            </Link>
          </div>
        )}

        {!checking && validSession && (
          <form onSubmit={handleSubmit} className="space-y-4 mt-5" noValidate>
            <div>
              <FieldLabel htmlFor="password" hint="6+ characters">
                New password
              </FieldLabel>
              <Input
                id="password"
                type={showPassword ? "text" : "password"}
                required
                minLength={6}
                autoComplete="new-password"
                autoFocus
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
            </div>

            {error && <Alert variant="error">{error}</Alert>}

            <Button type="submit" variant="primary" size="lg" disabled={loading} className="w-full">
              {loading ? (
                <>
                  <Loader2 size={16} className="animate-spin" /> Updating…
                </>
              ) : (
                "Update password"
              )}
            </Button>
          </form>
        )}
      </Card>
    </main>
  );
}
