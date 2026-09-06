"use client";

import { AppShell } from "@/components/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { Card } from "@/components/ui/card";
import { SignOutButton } from "@/components/SignOutButton";
import { useCurrentUser } from "@/hooks/useCurrentUser";

export default function SettingsPage() {
  const { email } = useCurrentUser();

  return (
    <AppShell>
      <main className="mx-auto max-w-3xl px-4 py-6 pb-16">
        <PageHeader title="Settings" description="Your account." />

        <Card className="p-4 flex items-center justify-between">
          <div>
            <p className="text-xs text-text-faint">Signed in as</p>
            <p className="text-sm text-text mt-0.5">{email ?? "…"}</p>
          </div>
          <SignOutButton />
        </Card>

        <p className="text-xs text-text-faint mt-4">
          Deeper settings (daily review cap, prayer-time convention, timezone) exist in the
          database (the <code>settings</code> table) but have no API or UI yet.
        </p>
      </main>
    </AppShell>
  );
}
