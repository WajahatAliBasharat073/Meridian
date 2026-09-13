"""Import the full Oxford 5000 (A1-C1) from the user's real Notion
export -- "The OXFORD 5000 Vocabulary CEFR Final.csv" at the repo root.

Unlike scripts/import_oxford_5000.py (which parses the three source
PDFs -- themselves only Oxford's "additional ~2000 words for B2-C1
learners" supplement), this CSV is the complete Oxford 5000 word list
across the full A1-C1 range: 5948 rows / 5946 unique (word, part of
speech) pairs, already one row per sense exactly like the app's schema
(e.g. "about" appears as two rows, adverb and preposition, both A1).
Every column matches a real vocab_words field 1:1 -- Word, Meaning
"Definition", Synonyms, Antonyms, Parts of Speech, Level "CEFR",
Example sentence, Word Patterns and Collocations, Paraphrase, Video or
Dictionary Link -- and, as in the user's live Notion tracker, only the
row for "a" has any of those extra fields actually filled in; every
other row is "Not started" with just word/part_of_speech/level.

This is expected to run *after* scripts/import_oxford_5000.py against
the same account: the two sources overlap on the B2/C1 range (2114 of
this CSV's pairs already exist from the PDF import) and occasionally
disagree on a word's level -- e.g. the American-English PDF lists
"autumn" as C1 (uncommon phrasing for American learners, who usually
say "fall") while this CSV, the unified master CEFR list, calls it A1.
vocab_repo.upsert_oxford_word always takes the level from whichever
import runs last, so running this CSV importer after the PDF one
corrects those ~22 conflicts in favor of the more complete, canonical
source. Two words genuinely have two same-part-of-speech senses at
different levels with no disambiguating text in this export ("lie"
verb: A1 for the horizontal-position sense, B1 for the tell-a-lie
sense; "march" noun: the proper-noun month vs. the common-noun parade,
which also collide once the word is lowercased for the dedup key) --
the (word, part_of_speech) dedup key can't tell those apart, so
whichever row is later in the CSV wins for that pair.

Usage:
    python -m scripts.import_oxford_5000_csv --user-id <uuid>
    python -m scripts.import_oxford_5000_csv --user-id <uuid> --apply
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import sys
import uuid as uuid_module
from dataclasses import dataclass
from pathlib import Path

from app.db import SessionLocal
from app.repositories import vocab as vocab_repo

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_CSV = _REPO_ROOT / "The OXFORD 5000 Vocabulary CEFR Final.csv"

_LEVELS = {"A1", "A2", "B1", "B2", "C1", "C2"}


@dataclass
class CsvRow:
    word: str
    part_of_speech: str | None
    cefr_level: str | None
    definition: str | None
    example_sentence: str | None
    synonyms: str | None
    antonyms: str | None
    word_patterns: str | None
    paraphrase: str | None
    dictionary_link: str | None


def _clean(value: str | None) -> str | None:
    if value is None:
        return None
    value = value.strip()
    return value or None


def _read_rows(csv_path: Path) -> list[CsvRow]:
    with open(csv_path, encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        rows: list[CsvRow] = []
        for raw in reader:
            word = _clean(raw.get("Word"))
            if not word:
                continue
            level = _clean(raw.get('Level "CEFR" '))
            if level is not None and level not in _LEVELS:
                level = None  # a handful of rows have stray/blank levels in the source export
            rows.append(
                CsvRow(
                    word=word,
                    part_of_speech=_clean(raw.get("Parts of Speech")),
                    cefr_level=level,
                    definition=_clean(raw.get('Meaning "Definition"')),
                    example_sentence=_clean(raw.get("Example sentence")),
                    synonyms=_clean(raw.get("Synonyms")),
                    antonyms=_clean(raw.get("Antonyms")),
                    word_patterns=_clean(raw.get("Word Patterns and Collocations")),
                    paraphrase=_clean(raw.get("Paraphrase")),
                    dictionary_link=_clean(raw.get("Video or Dictionary Link")),
                )
            )
        return rows


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-id", required=True, help="UUID of the user to import vocabulary for")
    parser.add_argument("--csv-path", default=str(_DEFAULT_CSV))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    user_id = uuid_module.UUID(args.user_id)
    rows = _read_rows(Path(args.csv_path))
    print(f"{len(rows)} usable row(s) found in {args.csv_path}.")

    if not args.apply:
        print("Dry run -- pass --apply to write to the database.")
        for r in rows[:15]:
            extra = f" -- {r.definition}" if r.definition else ""
            print(f"  {r.word} ({r.part_of_speech}, {r.cefr_level}){extra}")
        if len(rows) > 15:
            print(f"  ... and {len(rows) - 15} more")
        return

    created = updated = 0
    async with SessionLocal() as session:
        for r in rows:
            _, was_created = await vocab_repo.upsert_oxford_word(
                session,
                user_id,
                word=r.word,
                part_of_speech=r.part_of_speech,
                cefr_level=r.cefr_level,
                definition=r.definition,
                example_sentence=r.example_sentence,
                synonyms=r.synonyms,
                antonyms=r.antonyms,
                word_patterns=r.word_patterns,
                paraphrase=r.paraphrase,
                dictionary_link=r.dictionary_link,
            )
            if was_created:
                created += 1
            else:
                updated += 1

    print(f"Created {created}, updated {updated}, out of {len(rows)} rows.")


if __name__ == "__main__":
    asyncio.run(main())
