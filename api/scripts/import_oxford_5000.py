"""Import the Oxford 5000 British + American word lists (PDFs the user
placed at the repo root) into vocab_words.

Scope honesty: all three source PDFs describe the SAME list -- Oxford's
"additional 2000 words for B2-C1 learners" beyond the (unprovided)
Oxford 3000 core, not the full A1-C1 range the user's Notion tracker's
level tabs (A1/A2/B1/B2/C1) imply. Whatever this script writes only ever
covers B2/C1 words (plus a couple of B2 items, like "AIDS", Oxford filed
in this particular list) -- it cannot produce A1/A2/B1 rows that simply
aren't in the source material.

Three files exist at the repo root; only two are parsed:
    Oxford 5000.pdf                -- British English, alphabetical.
                                       Treated as authoritative.
    American_Oxford_5000.pdf       -- American English variant, mostly
                                       the same ~1990 words with a
                                       handful of spelling/level
                                       differences. Only contributes
                                       words genuinely absent from the
                                       British list.
    Oxford 5000_by CEFR level.pdf  -- the same British word set,
                                       resorted under level headings.
                                       Strictly less information per
                                       line than the alphabetical file
                                       above (no inline level marker on
                                       each word) and is a reformatting
                                       of it, not a separate source --
                                       not parsed here.

A dedicated `source` value ("oxford_5000_import") and a
(word, part_of_speech) dedup key (see vocab_repo.upsert_oxford_word)
keep this import safe to re-run and distinguishable from Notion-CSV or
manually typed rows.

Only three fields have real content in this source data: word,
part_of_speech, cefr_level. `definition` stays empty except for the
handful of words Oxford itself disambiguates with a parenthetical sense
hint inline in the list (e.g. "counter (argue against) v." vs "counter
(long flat surface) n.") -- that hint is real, sourced text, so it is
kept as `definition` for just those rows. Every other field the schema
now has room for (synonyms, antonyms, example_sentence, word_patterns,
paraphrase, dictionary_link) is left null for the user to fill in
themselves, exactly as their own Notion tracker shows for every row
except "a".

Usage:
    python -m scripts.import_oxford_5000 --user-id <uuid>
    python -m scripts.import_oxford_5000 --user-id <uuid> --apply
"""

from __future__ import annotations

import argparse
import asyncio
import re
import sys
import uuid as uuid_module
from dataclasses import dataclass
from pathlib import Path

from pypdf import PdfReader

from app.db import SessionLocal
from app.repositories import vocab as vocab_repo

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEFAULT_BRITISH_PDF = _REPO_ROOT / "Oxford 5000.pdf"
_DEFAULT_AMERICAN_PDF = _REPO_ROOT / "American_Oxford_5000.pdf"

_LEVELS = ("A1", "A2", "B1", "B2", "C1", "C2")
_LEVEL_RE = "|".join(_LEVELS)
_FIX_GLUED = re.compile(rf"\.({_LEVEL_RE})\b")
_FIX_COMMA_LEVEL = re.compile(rf",\s*({_LEVEL_RE})\b")
_LINE_ENDS_WITH_LEVEL = re.compile(rf"({_LEVEL_RE})$")
_SEGMENT_RE = re.compile(rf"^(?P<pos>.*?)\s+(?P<level>{_LEVEL_RE})$")
_SENSE_RE = re.compile(r"^\((?P<sense>[^)]+)\)\s*(?P<pos>.*)$")
_TRAILING_DIGIT = re.compile(r"^([A-Za-zÀ-ÿ\-]+)(\d)$")

# A bare abbreviation orphaned onto its own line by a PDF page/column
# break -- e.g. the American PDF wraps "strip (remove clothes/a layer)
# v. C1" across a page boundary and drops everything after "layer)" --
# must never be mistaken for a word of its own.
_BARE_POS_TOKENS = {"v.", "n.", "adj.", "adv.", "prep.", "pron.", "conj.", "adj./adv."}

_POS_NAMES = {
    "v.": "verb",
    "n.": "noun",
    "adj.": "adjective",
    "adv.": "adverb",
    "prep.": "preposition",
    "pron.": "pronoun",
    "conj.": "conjunction",
    "adj./adv.": "adjective/adverb",
    "number": "number",
}


@dataclass
class WordEntry:
    word: str
    part_of_speech: str | None
    cefr_level: str | None
    definition: str | None


def _expand_pos(raw_pos: str) -> tuple[str | None, str | None]:
    """Returns (part_of_speech, definition). Most rows have no
    parenthetical -- part_of_speech is just the abbreviation, expanded
    to a full word to match the Notion tracker's own presentation style.
    The handful of parenthetical-sense rows Oxford itself disambiguates
    (e.g. "counter") get the sense text back as a real, sourced
    definition rather than being discarded."""
    pos = raw_pos.strip()
    sense: str | None = None
    m = _SENSE_RE.match(pos)
    if m:
        sense = m.group("sense").strip()
        pos = m.group("pos").strip()
    name = _POS_NAMES.get(pos, pos or None)
    return name, sense


def _parse_pdf(path: Path) -> dict[str, list[WordEntry]]:
    reader = PdfReader(str(path))
    text = "\n".join(page.extract_text() for page in reader.pages)
    # A layout quirk in these PDFs sometimes drops the space between a
    # part-of-speech abbreviation and the level that follows it
    # ("fit n.C1"), and sometimes inserts a spurious comma directly
    # before a lone level with no second sense ("tragic adj., B2") --
    # both fixed globally before splitting into lines/segments.
    text = _FIX_GLUED.sub(r". \1", text)
    text = _FIX_COMMA_LEVEL.sub(r" \1", text)

    by_word: dict[str, list[WordEntry]] = {}
    for raw_line in text.split("\n"):
        line = raw_line.strip()
        if not line or not _LINE_ENDS_WITH_LEVEL.search(line):
            continue  # title/header/footer/instruction lines never end in a CEFR code
        parts = line.split(None, 1)
        if len(parts) != 2:
            continue
        word, rest = parts
        if word.lower() in _BARE_POS_TOKENS:
            continue  # an orphaned continuation line, not a real entry

        digit_match = _TRAILING_DIGIT.match(word)
        if digit_match:
            # Oxford's own homograph suffix (e.g. "bow1"); the user's
            # Notion schema has no place for it, and no other homograph
            # of the same word appears in this B2-C1 list to collide with.
            word = digit_match.group(1)

        entries: list[WordEntry] = []
        pending: list[str] = []
        for segment in rest.split(","):
            segment = segment.strip()
            if not segment:
                continue
            seg_match = _SEGMENT_RE.match(segment)
            if seg_match is None:
                pending.append(segment)
                continue
            level = seg_match.group("level")
            for pending_pos in pending:
                pos_name, definition = _expand_pos(pending_pos)
                entries.append(WordEntry(word, pos_name, level, definition))
            pos_name, definition = _expand_pos(seg_match.group("pos").strip())
            entries.append(WordEntry(word, pos_name, level, definition))
            pending = []
        by_word.setdefault(word, []).extend(entries)
    return by_word


def _merge(
    british: dict[str, list[WordEntry]], american: dict[str, list[WordEntry]]
) -> list[WordEntry]:
    """British is authoritative; American only contributes words genuinely
    absent from the British list (case-insensitive)."""
    british_lower = {w.lower() for w in british}
    merged: list[WordEntry] = []
    for entries in british.values():
        merged.extend(entries)
    for word, entries in american.items():
        if word.lower() not in british_lower:
            merged.extend(entries)
    return merged


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--user-id", required=True, help="UUID of the user to import vocabulary for")
    parser.add_argument("--british-pdf", default=str(_DEFAULT_BRITISH_PDF))
    parser.add_argument("--american-pdf", default=str(_DEFAULT_AMERICAN_PDF))
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    user_id = uuid_module.UUID(args.user_id)

    british = _parse_pdf(Path(args.british_pdf))
    american = _parse_pdf(Path(args.american_pdf))
    rows = _merge(british, american)
    print(
        f"{len(british)} British words, {len(american)} American words, "
        f"{len(rows)} (word, part of speech) rows to import."
    )

    if not args.apply:
        print("Dry run -- pass --apply to write to the database.")
        for r in rows[:15]:
            suffix = f" -- {r.definition}" if r.definition else ""
            print(f"  {r.word} ({r.part_of_speech}, {r.cefr_level}){suffix}")
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
            )
            if was_created:
                created += 1
            else:
                updated += 1

    print(f"Created {created}, updated {updated}, out of {len(rows)} rows.")


if __name__ == "__main__":
    asyncio.run(main())
