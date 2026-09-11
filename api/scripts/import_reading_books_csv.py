"""Import a reading library from a Notion database export.

Same situation as scripts/import_vocab_csv.py: no Notion API access exists
for this project (no API key configured, no Notion MCP tool available,
and the provided reading-tracker link is a private app.notion.com URL
WebFetch cannot read without an authenticated session). Notion's own
"Export > CSV" needs no API key and needs no code changes here to
support, so that's the integration this targets. Nothing in this script
invents a book, an author, or a rating -- every field comes from a column
in the CSV you provide.

Column names are matched case-insensitively and flexibly:

    title         <- Title | Book | Name
    author        <- Author | Writer
    status        <- Status  (mapped through _STATUS_ALIASES below --
                     Notion trackers commonly use labels like "Read" /
                     "Currently Reading" / "Want to Read" / "DNF" that
                     don't match this app's to_read/reading/completed/
                     paused/dropped enum verbatim)
    category      <- Genre | Category | Type
    rating        <- Rating | Score           (kept only if 1-5)
    total_pages   <- Pages | Total Pages | Page Count
    started_date  <- Started | Start Date | Date Started
    finished_date <- Finished | Finish Date | Date Finished | Date Read
    notes         <- Notes | Review | Thoughts
    priority      <- Priority                 (mapped through _PRIORITY_ALIASES)
    tags          <- Tags | Topics            (split on comma/semicolon)
    why_reading   <- Why | Reason
    cover_url     <- Cover | Cover Image | Cover URL

Re-running this on a re-exported CSV updates the matching existing book
(matched case-insensitively on title+author) rather than creating a
duplicate -- see life_logs_repo.find_book_by_title_author.

Usage:
    python -m scripts.import_reading_books_csv path/to/export.csv --user-id <uuid>
    python -m scripts.import_reading_books_csv path/to/export.csv --user-id <uuid> --apply
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import sys
import uuid as uuid_module
from dataclasses import dataclass, field
from datetime import date, datetime

from app.db import SessionLocal
from app.repositories import life_logs as life_logs_repo

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

_COLUMN_ALIASES: dict[str, tuple[str, ...]] = {
    "title": ("title", "book", "name"),
    "author": ("author", "writer"),
    "status": ("status",),
    "category": ("genre", "category", "type"),
    "rating": ("rating", "score"),
    "total_pages": ("pages", "total pages", "page count"),
    "started_date": ("started", "start date", "date started"),
    "finished_date": ("finished", "finish date", "date finished", "date read"),
    "notes": ("notes", "review", "thoughts"),
    "priority": ("priority",),
    "tags": ("tags", "topics"),
    "why_reading": ("why", "reason"),
    "cover_url": ("cover", "cover image", "cover url"),
}

_STATUS_ALIASES: dict[str, str] = {
    "read": "completed",
    "completed": "completed",
    "finished": "completed",
    "done": "completed",
    "currently reading": "reading",
    "reading": "reading",
    "in progress": "reading",
    "want to read": "to_read",
    "to read": "to_read",
    "backlog": "to_read",
    "planned": "to_read",
    "on hold": "paused",
    "paused": "paused",
    "dnf": "dropped",
    "did not finish": "dropped",
    "dropped": "dropped",
    "abandoned": "dropped",
}

_PRIORITY_ALIASES: dict[str, str] = {"high": "high", "medium": "medium", "med": "medium", "low": "low"}


def _build_column_map(headers: list[str]) -> dict[str, str]:
    lowered = {h.strip().lower(): h for h in headers}
    result: dict[str, str] = {}
    for field_name, aliases in _COLUMN_ALIASES.items():
        for alias in aliases:
            if alias in lowered:
                result[field_name] = lowered[alias]
                break
    return result


def _parse_date(value: str | None) -> date | None:
    if not value:
        return None
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%d/%m/%Y", "%B %d, %Y", "%b %d, %Y"):
        try:
            return datetime.strptime(value.strip(), fmt).date()
        except ValueError:
            continue
    return None


def _parse_rating(value: str | None) -> int | None:
    if not value:
        return None
    try:
        rating = int(float(value.strip()))
    except ValueError:
        return None
    return rating if 1 <= rating <= 5 else None


def _parse_page_count(value: str | None) -> int | None:
    if not value or not value.strip().isdigit():
        return None
    return int(value.strip())


@dataclass
class ImportBook:
    title: str
    author: str | None
    status: str
    category: str | None
    rating: int | None
    total_pages: int | None
    started_date: date | None
    finished_date: date | None
    notes: str | None
    priority: str | None
    tags: list[str] = field(default_factory=list)
    why_reading: str | None = None
    cover_url: str | None = None


def _read_rows(csv_path: str) -> list[ImportBook]:
    with open(csv_path, newline="", encoding="utf-8-sig") as f:
        reader = csv.DictReader(f)
        headers = list(reader.fieldnames or [])
        column_map = _build_column_map(headers)
        if "title" not in column_map:
            raise SystemExit(
                f"Couldn't find a title/book/name column in {csv_path}. Headers found: {headers}"
            )

        def cell(raw: dict[str, str], field_name: str) -> str | None:
            column = column_map.get(field_name)
            if column is None:
                return None
            return (raw.get(column) or "").strip() or None

        books: list[ImportBook] = []
        for raw in reader:
            title = cell(raw, "title")
            if not title:
                continue
            status_raw = (cell(raw, "status") or "").lower()
            priority_raw = (cell(raw, "priority") or "").lower()
            tags_raw = cell(raw, "tags")
            books.append(
                ImportBook(
                    title=title,
                    author=cell(raw, "author"),
                    status=_STATUS_ALIASES.get(status_raw, "to_read"),
                    category=cell(raw, "category"),
                    rating=_parse_rating(cell(raw, "rating")),
                    total_pages=_parse_page_count(cell(raw, "total_pages")),
                    started_date=_parse_date(cell(raw, "started_date")),
                    finished_date=_parse_date(cell(raw, "finished_date")),
                    notes=cell(raw, "notes"),
                    priority=_PRIORITY_ALIASES.get(priority_raw),
                    tags=[t.strip() for t in tags_raw.replace(";", ",").split(",") if t.strip()]
                    if tags_raw
                    else [],
                    why_reading=cell(raw, "why_reading"),
                    cover_url=cell(raw, "cover_url"),
                )
            )
        return books


async def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("csv_path")
    parser.add_argument("--user-id", required=True)
    parser.add_argument("--apply", action="store_true")
    args = parser.parse_args()

    user_id = uuid_module.UUID(args.user_id)
    books = _read_rows(args.csv_path)
    print(f"{len(books)} usable row(s) found in {args.csv_path}.")

    if not args.apply:
        print("Dry run -- pass --apply to write to the database.")
        for b in books[:15]:
            print(f"  {b.title} by {b.author or 'unknown'} -- status={b.status}")
        if len(books) > 15:
            print(f"  ... and {len(books) - 15} more")
        return

    created = updated = 0
    async with SessionLocal() as session:
        for b in books:
            existing = await life_logs_repo.find_book_by_title_author(session, user_id, b.title, b.author)
            if existing is not None:
                fields: dict[str, object] = {
                    "status": b.status,
                    "category": b.category,
                    "rating": b.rating,
                    "total_pages": b.total_pages,
                    "started_date": b.started_date,
                    "finished_date": b.finished_date,
                    "notes": b.notes,
                    "priority": b.priority,
                    "tags": b.tags or None,
                    "why_reading": b.why_reading,
                    "cover_url": b.cover_url,
                }
                await life_logs_repo.update_reading_book(
                    session, user_id, existing.id, {k: v for k, v in fields.items() if v is not None}
                )
                updated += 1
            else:
                await life_logs_repo.create_reading_book(
                    session, user_id, b.title, b.author, b.cover_url, b.total_pages,
                    "book", b.category, b.status, b.started_date, b.priority, b.tags, b.why_reading,
                )
                created += 1

    print(f"Created {created}, updated {updated}, out of {len(books)} rows.")


if __name__ == "__main__":
    asyncio.run(main())
