import { FlaskConical } from "lucide-react";
import { ComingSoon } from "@/components/layout/ComingSoon";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";

export default function ResearchPage() {
  return (
    <PageContainer>
      <PageHeader
        eyebrow="Learning"
        title="Research"
        description="Thesis work log — milestones, deadlines, and output."
      />
      <ComingSoon
        icon={FlaskConical}
        title="Research"
        description="Thesis log rows already have a schema (milestone, summary, minutes, deadline, status). This screen stays empty until those rows can be read and written through the API."
      />
    </PageContainer>
  );
}
