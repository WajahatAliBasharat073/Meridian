import { BookOpen } from "lucide-react";
import { AppShell } from "@/components/AppShell";
import { PageHeader } from "@/components/layout/PageHeader";
import { EmptyState } from "@/components/ui/empty-state";

export default function ReadingPage() {
  return (
    <AppShell>
      <main className="mx-auto max-w-3xl px-4 py-6 pb-16">
        <PageHeader title="Reading" description="Book and paper log." />
        <EmptyState
          icon={BookOpen}
          title="Not built yet"
          description="The reading_log table exists (title, author, kind, progress, status) but has no API endpoints or UI. Needs: a repository + router, then this page wired to it."
        />
      </main>
    </AppShell>
  );
}
