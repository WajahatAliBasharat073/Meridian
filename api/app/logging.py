"""Structured logging.

Nothing in this codebase logged anything before this — no auth-failure
trail, no record of a failed LLM call, no way to reconstruct what
happened after the fact. `structlog` was already a pinned dependency,
unused. This wires it up once, at import time, and gives every module a
plain `get_logger(__name__)` — key-value structured output to stdout
(JSON in a real deployment would just mean swapping the renderer here,
not touching any call site).

Never log a secret or a full token/JWT — auth failures below log the
failure reason and a truncated token prefix at most, matching the
existing rule that `GROQ_API_KEY` (and any per-user key) never leaves
the process it's read into.
"""

from __future__ import annotations

import logging
import sys

import structlog

_configured = False


def configure_logging() -> None:
    global _configured
    if _configured:
        return

    logging.basicConfig(format="%(message)s", stream=sys.stdout, level=logging.INFO)

    structlog.configure(
        processors=[
            structlog.contextvars.merge_contextvars,
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.StackInfoRenderer(),
            structlog.dev.ConsoleRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(logging.INFO),
        logger_factory=structlog.PrintLoggerFactory(),
        cache_logger_on_first_use=True,
    )
    _configured = True


def get_logger(name: str) -> structlog.typing.FilteringBoundLogger:
    configure_logging()
    logger: structlog.typing.FilteringBoundLogger = structlog.get_logger(name)
    return logger
