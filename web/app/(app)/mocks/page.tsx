import { Mic } from "lucide-react";
import { ComingSoon } from "@/components/layout/ComingSoon";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";

export default function MocksPage() {
  return (
    <PageContainer>
      <PageHeader
        eyebrow="Career"
        title="Mocks"
        description="Mock interview log — coding, ML, system design, communication."
      />
      <ComingSoon
        icon={Mic}
        title="Mocks"
        description="The database already has a place for mock rounds (date, company mode, scores, weakness, next action). Logging them here waits on an API that is not built yet."
      />
    </PageContainer>
  );
}
