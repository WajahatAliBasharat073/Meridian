import { FlaskConical } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyState } from "@/components/ui/empty-state";

export default function ResearchPage() {
  return (
    <AppShell>
      <main className="mx-auto max-w-3xl px-4 py-6 pb-16">
        <PageHeader title="Research" description="Thesis work log — milestones, deadlines, output." />
        <EmptyState
          icon={FlaskConical}
          title="Not built yet"
          description="The thesis_log table exists (milestone, work summary, minutes, output type, deadline, status) but has no API endpoints or UI. Needs: a repository + router, then this page wired to it."
        />
      </main>
    </AppShell>
  );
}
