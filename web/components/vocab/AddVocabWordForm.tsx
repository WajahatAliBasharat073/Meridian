"use client";

import { useState } from "react";
import { Plus } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { useCreateVocabWord } from "@/hooks/useVocab";
import { ApiError } from "@/lib/api";

export function AddVocabWordForm() {
  const [open, setOpen] = useState(false);
  const [word, setWord] = useState("");
  const [definition, setDefinition] = useState("");
  const [exampleSentence, setExampleSentence] = useState("");
  const [partOfSpeech, setPartOfSpeech] = useState("");
  const [error, setError] = useState<string | null>(null);
  const createWord = useCreateVocabWord();

  if (!open) {
    return (
      <div className="flex justify-end mb-4">
        <Button variant="primary" size="md" onClick={() => setOpen(true)} className="gap-1.5">
          <Plus size={15} /> Add Word
        </Button>
      </div>
    );
  }

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError(null);
    if (!word.trim() || !definition.trim()) return;
    createWord.mutate(
      {
        word: word.trim(),
        definition: definition.trim(),
        example_sentence: exampleSentence.trim() || undefined,
        part_of_speech: partOfSpeech.trim() || undefined,
      },
      {
        onSuccess: () => {
          setWord("");
          setDefinition("");
          setExampleSentence("");
          setPartOfSpeech("");
          setOpen(false);
        },
        onError: (err) => {
          setError(err instanceof ApiError ? err.message : "Couldn't add that word.");
        },
      }
    );
  };

  return (
    <Card className="p-5 mb-4 border-accent/40 bg-gradient-to-b from-surface to-surface-2">
      <form onSubmit={handleSubmit} className="space-y-3">
        <h3 className="text-sm font-semibold text-text">Add a Word</h3>
        <div className="grid sm:grid-cols-2 gap-2">
          <Input placeholder="Word" value={word} onChange={(e) => setWord(e.target.value)} required />
          <Input
            placeholder="Part of speech (optional)"
            value={partOfSpeech}
            onChange={(e) => setPartOfSpeech(e.target.value)}
          />
        </div>
        <Input
          placeholder="Definition"
          value={definition}
          onChange={(e) => setDefinition(e.target.value)}
          required
        />
        <Input
          placeholder="Example sentence (optional)"
          value={exampleSentence}
          onChange={(e) => setExampleSentence(e.target.value)}
        />
        {error && <p className="text-xs text-danger">{error}</p>}
        <div className="flex justify-end gap-2 pt-1">
          <Button type="button" variant="ghost" size="sm" onClick={() => setOpen(false)}>
            Cancel
          </Button>
          <Button
            type="submit"
            variant="primary"
            size="sm"
            disabled={createWord.isPending || !word.trim() || !definition.trim()}
          >
            {createWord.isPending ? "Saving…" : "Add Word"}
          </Button>
        </div>
      </form>
    </Card>
  );
}
