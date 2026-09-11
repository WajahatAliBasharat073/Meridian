"use client";

import { AddVocabWordForm } from "@/components/vocab/AddVocabWordForm";
import { VocabFlashcards } from "@/components/vocab/VocabFlashcards";
import { VocabSummaryCard } from "@/components/vocab/VocabSummaryCard";
import { PageContainer } from "@/components/layout/PageContainer";
import { PageHeader } from "@/components/layout/PageHeader";

export default function VocabularyPage() {
  return (
    <PageContainer>
      <PageHeader
        eyebrow="Language"
        title="English Vocabulary"
        description="A daily review of words worth knowing -- prioritizes what you've flagged to revisit, then what you haven't reviewed yet."
      />
      <VocabSummaryCard />
      <AddVocabWordForm />
      <VocabFlashcards />
    </PageContainer>
  );
}
