"use client";

import Link from "next/link";
import { useState } from "react";
import { ArrowLeft, Loader2, Mail } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { FieldLabel } from "@/components/ui/field-label";
import { Alert } from "@/components/ui/alert";
import { createClient } from "@/lib/supabase/client";

export default function ForgotPasswordPage() {
  const [email, setEmail] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [sent, setSent] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    setLoading(true);

    const supabase = createClient();
    const { error: authError } = await supabase.auth.resetPasswordForEmail(email, {
      redirectTo: `${window.location.origin}/auth/callback?next=/reset-password`,
    });

    setLoading(false);
    if (authError) {
      setError(authError.message);
      return;
    }
    setSent(true);
  };

  return (
    <main className="min-h-screen flex items-center justify-center px-4">
      <Card className="w-full max-w-sm p-6">
        <Link
          href="/login"
          className="inline-flex items-center gap-1.5 text-sm text-text-muted hover:text-text mb-6"
        >
          <ArrowLeft size={14} /> Back to sign in
        </Link>

        <h1 className="text-xl font-semibold text-text mb-1">Reset your password</h1>
        <p className="text-sm text-text-muted mb-6">
          Enter your email and we&apos;ll send you a link to set a new one.
        </p>

        {sent ? (
          <Alert variant="success">
            Check {email} for a reset link — it&apos;s valid for a limited time.
          </Alert>
        ) : (
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

            {error && <Alert variant="error">{error}</Alert>}

            <Button type="submit" variant="primary" size="lg" disabled={loading} className="w-full">
              {loading ? (
                <>
                  <Loader2 size={16} className="animate-spin" /> Sending…
                </>
              ) : (
                "Send reset link"
              )}
            </Button>
          </form>
        )}
      </Card>
    </main>
  );
}
