"use client";

import { useState } from "react";
import { Eye, EyeOff } from "lucide-react";
import { Input } from "@/components/ui/input";
import { useUpdateVocabWord } from "@/hooks/useVocab";
import type { VocabWordOut, VocabWordUpdateInput } from "@/lib/types";

type FieldKey = "definition" | "synonyms" | "antonyms" | "example_sentence" | "notes";

const FIELDS: { key: FieldKey; label: string; placeholder: string }[] = [
  { key: "definition", label: "Definition", placeholder: "What does it mean?" },
  { key: "synonyms", label: "Synonyms", placeholder: "Words that mean the same" },
  { key: "antonyms", label: "Antonyms", placeholder: "Opposite words" },
  { key: "example_sentence", label: "Example sentence", placeholder: "Use it in a sentence" },
  { key: "notes", label: "Notes", placeholder: "Anything else worth remembering" },
];

/** One row per word field, editable in place. A field that already has
 * content starts masked like a password -- an eye icon reveals it -- so
 * revisiting a word tests recall before showing the answer; an empty
 * field starts revealed since there is nothing yet to test against. */
export function VocabWordDetailsPanel({ word }: { word: VocabWordOut }) {
  const updateWord = useUpdateVocabWord();

  return (
    <div className="mt-4 space-y-3 text-left max-w-xl mx-auto">
      {FIELDS.map((f) => (
        <RevealableField
          key={f.key}
          label={f.label}
          placeholder={f.placeholder}
          value={word[f.key] ?? ""}
          onSave={(next) => {
            const input = { [f.key]: next || null } as VocabWordUpdateInput;
            updateWord.mutate({ wordId: word.id, input });
          }}
        />
      ))}
    </div>
  );
}

function RevealableField({
  label,
  placeholder,
  value,
  onSave,
}: {
  label: string;
  placeholder: string;
  value: string;
  onSave: (next: string) => void;
}) {
  const [draft, setDraft] = useState(value);
  const [revealed, setRevealed] = useState(!value);

  return (
    <div>
      <label className="text-[10px] uppercase tracking-wide text-text-faint">{label}</label>
      <Input
        type={revealed ? "text" : "password"}
        value={draft}
        onChange={(e) => setDraft(e.target.value)}
        onBlur={() => {
          if (draft !== value) onSave(draft);
        }}
        placeholder={placeholder}
        className="h-10 text-sm mt-1"
        trailing={
          <button
            type="button"
            onClick={() => setRevealed((r) => !r)}
            aria-label={revealed ? `Hide ${label.toLowerCase()}` : `Show ${label.toLowerCase()}`}
            className="h-8 w-8 flex items-center justify-center rounded-md text-text-faint hover:text-text hover:bg-surface-hover"
          >
            {revealed ? <EyeOff size={15} /> : <Eye size={15} />}
          </button>
        }
      />
    </div>
  );
}
