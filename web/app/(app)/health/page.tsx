import { HeartPulse } from "lucide-react";
import { ComingSoon } from "@/components/layout/ComingSoon";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";

export default function HealthPage() {
  return (
    <PageContainer>
      <PageHeader
        eyebrow="Wellbeing"
        title="Recovery"
        description="Sleep, energy, mood, stress, water, and nutrition — when logging exists."
      />
      <ComingSoon
        icon={HeartPulse}
        title="Recovery"
        description="Recovery and nutrition logs exist in the database. There is no endpoint to read or write them yet, so this page does not invent charts or sample days."
      />
    </PageContainer>
  );
}
