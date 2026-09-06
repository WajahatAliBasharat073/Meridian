import { Mic } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyState } from "@/components/ui/empty-state";

export default function MocksPage() {
  return (
    <AppShell>
      <main className="mx-auto max-w-3xl px-4 py-6 pb-16">
        <PageHeader title="Mocks" description="Mock interview log — coding, ML, system design, communication." />
        <EmptyState
          icon={Mic}
          title="Not built yet"
          description="The mocks table exists (date, company mode, round type, scores per dimension, top weakness, next action) but has no API endpoints or UI. Needs: a repository + POST/GET router, then this page wired to it — same pattern as Problems."
        />
      </main>
    </AppShell>
  );
}
