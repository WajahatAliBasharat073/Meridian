import { HeartPulse } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyState } from "@/components/ui/empty-state";

export default function HealthPage() {
  return (
    <AppShell>
      <main className="mx-auto max-w-3xl px-4 py-6 pb-16">
        <PageHeader title="Recovery & Nutrition" description="Sleep, energy, mood, stress, water, and nutrition trends." />
        <EmptyState
          icon={HeartPulse}
          title="Not built yet"
          description="recovery_log and nutrition_log both exist (sleep hours/quality, energy, mood, stress, water, calories, protein) but have no API endpoints or UI. Needs: a repository + router for each, then this page wired to them."
        />
      </main>
    </AppShell>
  );
}
