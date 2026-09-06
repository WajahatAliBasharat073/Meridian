import { BookOpen } from "lucide-react";
import { ComingSoon } from "@/components/layout/ComingSoon";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";

export default function ReadingPage() {
  return (
    <PageContainer>
      <PageHeader
        eyebrow="Learning"
        title="Reading"
        description="Book and paper log — title, author, progress, status."
      />
      <ComingSoon
        icon={BookOpen}
        title="Reading"
        description="Reading entries can be stored, but there is no API to list or add them yet. This page will become the log when that ships — it is not a placeholder for a different product."
      />
    </PageContainer>
  );
}
