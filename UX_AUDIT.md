# UX Audit

## 1. Page inventory (what each route actually does, verified by reading, not guessed from the folder name)

| Route | Actual content |
|---|---|
| `today` | Sticky two-column daily command center: left rail of stacked widgets (greeting, time progress, vitals, theory picks, recommendations, bandwidth, reflection), right column a single day timeline. |
| `dashboard` | 4-tab analytics hub (Overview / Time & Focus / Learning Curve / Behavioral Patterns) — KPI grid, consistency heatmap, recharts-based trend charts. |
| `plan` | Weekly time-budget planner (minutes-per-category CRUD against `time_budgets`) plus a hardcoded reference schedule. |
| `problems` | DSA topic browser with a build→defend verification gate per topic. |
| `curriculum` | Interview-question module browser, P0–P3 priority chips. |
| `concepts` | ML/GenAI roadmap — category tiles with counts, links into daily theory. |
| `coach` | Full threaded chat UI (localStorage-persisted threads) against the Groq-backed assistant. |
| `goals` | Flat goal list, manual progress slider, optional activity-category link. |
| `health` | Vitals: sleep/water/energy/recovery cards. |
| `reading` | Book log with sessions, status/format/category enums. |
| `research` | Bare thesis work-log (milestone/minutes/output-type), explicitly computed-not-invented stats. |
| `resources` | Static curated link library, search + category grouping. |
| `weekly-review` | Read-only 7-day rollup. |
| `settings` | Account info, sound, AI settings. |
| `mocks` | **Placeholder only** — renders `<ComingSoon>`, states the backing API isn't built. |

**Observation**: there is no dedicated career page (applications, interviews, portfolio) anywhere in the route tree — confirmed by both the route listing and a repo-wide content search. If Career becomes a real section later, it has no existing home to extend; it would be new, not a gap in an existing page.

## 2. Navigation

Fully data-driven: `lib/nav.ts`'s `NAV_GROUPS` array, each item `{href, label, icon, soon?, primary?}`. Single-item groups render as flat top-level links (Today, Plan, Coach); multi-item groups render as a dropdown (e.g. "Learn"). Mobile gets a hamburger drawer plus a bottom tab bar showing only `primary: true` items. A `soon?` flag already exists for shipping a nav entry ahead of its backing page (renders a "Soon" pill) — exactly the mechanism `mocks` should be using consistently with any future Finance rollout that ships incrementally. Adding a new top-level "Finance" section is a one-line config change, not a structural one.

## 3. Design system consistency

Genuinely consistent, not superficially so:
- **States**: every audited page (dashboard, today, goals, health, curriculum, problems, reading, research, weekly-review) uses the same triad — `Skeleton` while loading, `QueryError` (auth/network-aware, shared) on error, `EmptyState` or an inline "nothing yet" card when data is empty. The one deliberate deviation is `today`'s richer first-run `WelcomeState`, intentional for the app's primary screen.
- **Tokens**: dark-only palette via CSS custom properties (`--surface`, `--text-*`, `--accent*`, `--status-done/-partial/-rescheduled`, a 7-step `--mastery-l0..l6` scale, semantic aliases `--danger`/`--warning`/`--info` deliberately kept distinct from raw hues "so call sites read as intent, not reuse"). A Finance module should express over/under-budget state through `--status-done`/`--danger` rather than inventing new red/green literals.
- **Charts**: one library (`recharts`), one wrapper (`ChartCard`) that structurally forces every chart to answer a stated question with a written takeaway and an explicit empty state — this is the right pattern to hold Finance spending charts to as well, directly addressing the spec's "avoid meaningless dashboards full of graphs" concern.

## 4. Gaps

- **No generic `Table`, `Dialog`/`Modal`, or `Tabs` primitive** — each page that needs one hand-rolls its own (dashboard's tabs are inline buttons; `problems` has a one-off dialog). Not urgent today; the moment Finance needs a transaction table or an "add transaction" modal, that's the natural trigger to extract a shared primitive rather than add a third bespoke implementation.
- **No global search.** Nothing crosses domains today (questions, notes, research logs, resources are each searched, if at all, only within their own page — `resources` has an in-page search, nothing else does). Worth deferring until there are enough cross-domain entities (Finance transactions, goals, research notes) to make a unified search worth its complexity — premature today.
- **`mocks` is a naked placeholder** with no real UX plan yet — fine as-is, just noting it's not "done," it's parked.
- **The Goal card/progress-bar UI is reusable for Finance goals visually, but the underlying model isn't** (see `DATA_MODEL_AUDIT.md` §3) — the UI pattern (progress bar + badge + "update progress" button) should be reused for a `finance_goals` card even though the backend model is new.

## 5. Verdict

The product does not feel like glued-together features today — navigation, states, tokens, and charting are centrally governed, not per-page decisions. The risk with adding Finance (and later Career, unified dashboard, AI assistant) is losing that discipline by introducing a second design language under time pressure. The concrete guardrail: any new page must be built from the existing `Card`/`Button`/`Badge`/`Skeleton`/`QueryError`/`EmptyState`/`ChartCard` set and the existing `lib/api.ts`/`lib/types.ts`/`lib/nav.ts` conventions before anything new is introduced.
