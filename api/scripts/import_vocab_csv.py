"""Import vocabulary from a Notion database export.

No Notion API access exists for this project (checked: no API key
anywhere in .env/.env.example, no Notion MCP tool available, and the
provided page link is a private app.notion.com URL that cannot be
fetched without authenticated access). Notion's own "Export > CSV" on
any database requires no API key and needs no code changes here to
support -- so that is the integration this script targets, not a live
API sync. Nothing in this script invents word data; every row it writes
comes from a column in the CSV you provide.

Column names are matched case-insensitively and flexibly, since a Notion
export's exact header text depends on how the database's properties were
named:

    word            <- Word | Term | Name
    definition      <- Definition | Meaning
    example_sentence <- Example | Example Sentence | Sentence
    pronunciation   <- Pronunciation | IPA
    part_of_speech  <- Part of Speech | POS | Type
    category        <- Category | Tag | Tags
    notion_page_id  <- a "Notion ID"/"ID" column if the export includes
                       one (some export configurations do); if absent,
                       de-dup falls back to a case-insensitive match on
                       `word` alone, per-user.

Re-running this on a re-exported CSV updates existing rows (matched by
notion_page_id, or by word if no id column) rather than creating
duplicates.

Usage:
    python -m scripts.import_vocab_csv path/to/export.csv --user-id <uuid>
    python -m scripts.import_vocab_csv path/to/export.csv --user-id <uuid> --apply
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import sys
import uuid as uuid_module
from dataclasses import dataclass

from app.db import SessionLocal
from app.repositories import vocab as vocab_repo

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "word": ("word", "term", "name"),
    "definition": ("definition", "meaning"),
    "example_sentence": ("example", "example sentence", "sentence"),
    "pronunciation": ("pronunciation", "ipa"),
    "part_of_speech": ("part of speech", "pos", "type"),
    "category": ("category", "tag", "tags"),
    "notion_page_id": ("notion id", "id", "page id"),
}


def _build_column_map(headers: list[str]) -> dict[str, str]:
    """field name -> actual CSV header, for whichever alias matched."""
    lowered = {h.strip().lower(): h for h in headers}
    result: dict[str, str] = {}
    for field, aliases in _COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in lowered:
                result[field] = lowered[alias]
                break
    return result


@dataclass
class ImportRow:
    word: str
    definition: str
    example_sentence: str | None
    pronunciation: str | None
    part_of_speech: str | None
    category: str | None
    notion_page_id: str | None


def _read_rows(csv_path: str) -> list[ImportRow]:
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = list(reader.fieldnames or [])
        column_map = _build_column_map(headers)
        if "word" not in column_map:
            raise SystemExit(
                f"Couldn't find a word/term/name column in {csv_path}. "
                f"Headers found: {headers}"
            )
        if "definition" not in column_map:
            raise SystemExit(
                f"Couldn't find a definition/meaning column in {csv_path}. "
                f"Headers found: {headers}"
            )

        def optional(field: str) -> str | None:
            column = column_map.get(field)
            if column is None:
                return None
            return raw.get(column, "").strip() or None

        rows: list[ImportRow] = []
        for raw in reader:
            word = raw.get(column_map["word"], "").strip()
            definition = raw.get(column_map["definition"], "").strip()
            if not word or not definition:
                continue  # a blank row in the export -- not a real entry
            rows.append(
                ImportRow(
                    word=word,
                    definition=definition,
                    example_sentence=optional("example_sentence"),
                    pronunciation=optional("pronunciation"),
                    part_of_speech=optional("part_of_speech"),
                    category=optional("category"),
                    notion_page_id=optional("notion_page_id"),
                )
            )
        return rows


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--user-id", required=True, help="UUID of the user to import vocabulary for")
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    user_id = uuid_module.UUID(args.user_id)
    rows = _read_rows(args.csv_path)
    print(f"{len(rows)} usable row(s) found in {args.csv_path}.")

    if not args.apply:
        print("Dry run -- pass --apply to write to the database.")
        for r in rows[:10]:
            print(f"  {r.word}: {r.definition[:60]}")
        if len(rows) > 10:
            print(f"  ... and {len(rows) - 10} more")
        return

    created = updated = 0
    async with SessionLocal() as session:
        for r in rows:
            _, was_created = await vocab_repo.upsert_from_import(
                session,
                user_id,
                word=r.word,
                definition=r.definition,
                example_sentence=r.example_sentence,
                pronunciation=r.pronunciation,
                part_of_speech=r.part_of_speech,
                category=r.category,
                notion_page_id=r.notion_page_id,
            )
            if was_created:
                created += 1
            else:
                updated += 1

    print(f"Created {created}, updated {updated}, out of {len(rows)} rows.")


if __name__ == "__main__":
    asyncio.run(main())
