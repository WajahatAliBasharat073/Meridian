# Security & Privacy Audit

Scope: authorization, user isolation, secrets handling, logging, error handling, test coverage, data lifecycle. This matters more than usual because a Finance module will store real financial data and an AI assistant is planned that will read across domains.

## Findings that were checked and are CORRECT (no action needed)

1. **No IDOR pattern found.** Every router obtains `user_id` exclusively from `Depends(get_current_user_id)` (JWT `sub` claim), never from a request body/query/path parameter. Checked across every router (`attempts`, `blocks`, `concepts`, `curriculum`, `daily_recap`, `focus_sessions`, `goals`, `life_logs`, `problems`, `profile`, `ai_settings`, `coach`, `today`, `verification`, `vitals`) — the pattern holds with zero exceptions.
2. **No committed secrets.** Only `api/.env.example` is tracked; real `.env` files are excluded by `.gitignore`. No file with "credential"/"secret"/"key" in its name was found anywhere in the repo outside `.venv`/`node_modules`.
3. **Secrets never echoed back.** `ai_settings.py`'s per-user Groq key is stored inside `user.settings["ai"]["groq_api_key"]` but the API response only ever returns `api_key_set: bool` — the raw value is never serialized into any response, verified by reading the full output-model construction.
4. **RLS is applied consistently** (all 15 user-scoped tables, identical templated policy) as defense-in-depth, with the one real gotcha (a view running with elevated privilege) already closed via `security_invoker=true` on `current_mastery`.
5. **No unhandled-exception stack-trace leakage.** FastAPI's default 500 handler returns a generic `{"detail": "Internal Server Error"}`; no router sets `debug=True`.

## Findings that need action

| Priority | Finding | Why it matters | Fix |
|---|---|---|---|
| P0 | **`curriculum_topics` has no RLS policy**, unlike every other reference table. | Inconsistency in an otherwise airtight pattern — low blast radius today (non-sensitive, and RLS is defense-in-depth only) but should be closed before it's forgotten and copy-pasted into a sensitive table by habit. | One-line migration adding the same read-only reference-table policy every other reference table gets. |
| P0 | **Zero structured logging anywhere in the codebase.** No `logging.getLogger`, no request logging, no audit trail for auth failures, LLM calls, or mutations. `coach.py`'s `except Exception:` around the Groq call swallows failures completely silently. | Before Finance data lands (money mutations, in particular, should be auditable) and before the AI assistant reads more of the app's data, there is no way to reconstruct what happened after the fact. | Add `structlog` (already a pinned dependency, unused) at the repository-write layer at minimum; log auth failures and LLM-call outcomes. |
| P0 | **No cross-user isolation test exists.** All 18 test files are engine unit tests; none spins up two accounts and asserts isolation. | RLS is bypassed by the API's own DB role, so the repository layer's `user_id` threading is the *only* real enforcement — and it is completely untested. This is the single most consequential gap before real financial data is stored. | Add one integration test suite that creates two users and asserts every list/get endpoint returns zero cross-contamination. |
| P1 | **No account-deletion or data-export endpoint.** | Not a bug today, but a real gap for a product that will hold financial, career, and research data, ahead of it having more than one real user. | Defer implementation, but scope it now: a single `DELETE /api/account` + `GET /api/account/export` pair, cascading through every `user_id`-scoped table. |
| P2 | **In-memory auth caches (`_known_user_ids`, JWKS cache) are unbounded and process-local.** | Fine for a single-instance/single-user deployment; would need a size bound and invalidation strategy if the deployment ever scales past one worker or many users. | Defer — not a problem at current scale. |

## Specific guidance for the Finance module

Because Finance is the first genuinely sensitive data domain in this app:
- Follow the exact same `user_id` + `Depends(get_current_user_id)` pattern with zero exceptions — this audit found the pattern is currently applied with perfect consistency, and that consistency is the app's actual security boundary (not RLS).
- Add the audit trail (structured logging on every finance mutation) as part of Finance's own migration, not deferred with the rest of the app — a modified/deleted transaction should be reconstructable.
- Do not build bank-integration/scraping in this phase (per the module proposal) — that would introduce a genuinely new class of secret (bank credentials/OAuth tokens) that the current secrets-handling pattern has never had to deal with, and this audit found no infrastructure for that (no encryption-at-rest discussion, no secrets vault) — manual-first entry avoids the question entirely for now.
