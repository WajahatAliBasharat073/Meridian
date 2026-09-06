# Release Engineering Setup

## Current-State Audit

Observed locally on this repository:

- Repository: single monorepo named `Meridian`.
- Current branch: `main`.
- Remote branch refs: `origin/main` only.
- Local default remote HEAD: not configured (`refs/remotes/origin/HEAD` is missing).
- Remote URL: `git@github-personal:WajahatAliBasharat073/Meridian.git`.
- Remote inspection failed locally because the SSH host alias `github-personal` is not resolvable in this shell.
- Tags: none.
- Commit history: six linear commits, all on `main`.
- Frontend and backend share the same repository and same branch.
- No dedicated `develop`, `staging`, `qa`, `uat`, `release/*`, or `hotfix/*` branches exist.
- No evidence of merge commits, release tags, or a formal PR/release process in Git history.
- Infrastructure in Git: local `docker-compose.yml` for Postgres only.
- Backend: FastAPI in `api/`, Python 3.12, Alembic, Supabase/Postgres-oriented configuration.
- Frontend: Next.js in `web/`, App Router, TypeScript, server-side API proxy.
- Runtime secret templates are present in `api/.env.example` and `web/.env.example`.
- Real secrets are ignored by Git through root and web `.gitignore` files.

## Decision

Use a trunk-based monorepo strategy:

- `main` is the single protected integration branch.
- Short-lived branches are used for work: `feature/*`, `bugfix/*`, `hotfix/*`, and optionally `chore/*`.
- Production releases are created from immutable tags: `vMAJOR.MINOR.PATCH`.
- Do not add permanent `develop`, `staging`, `qa`, or `uat` branches at this stage.

This is the best fit for the current project because the repo is young, the team appears small, frontend and backend are tightly coupled, and there is no evidence of long-lived parallel release trains. Permanent environment branches would add merge overhead without solving a current operational problem.

## Branches vs Environments

Branches are code organization and review boundaries. Environments are deployed runtime targets. They do not need to map one-to-one.

Recommended environment model:

| Environment | Source | Purpose |
| --- | --- | --- |
| Local Development | developer machine | Fast iteration with local `.env` files |
| Pull Request Preview | PR branch | Optional web/API preview after hosting is chosen |
| Staging | latest protected `main` | Production-like validation before release |
| Production | signed/versioned `v*.*.*` tag | User-facing stable release |

QA/UAT should be GitHub Environments or preview deployments, not permanent branches, unless a larger team later needs long-running acceptance windows.

## Workflow Files

| File | Workflow name | Purpose |
| --- | --- | --- |
| `.github/workflows/pull-request-quality.yml` | `Pull Request Quality Gate` | Detect changed paths, run relevant backend/frontend/platform checks, and emit one required final status |
| `.github/workflows/security-scanning.yml` | `Security Scanning` | CodeQL analysis for Python and TypeScript |
| `.github/workflows/deploy-staging.yml` | `Deploy Staging` | Validate `main`, then deploy to staging when provider hooks are configured |
| `.github/workflows/deploy-production.yml` | `Deploy Production` | Deploy version tags or approved manual refs to production |
| `.github/dependabot.yml` | Dependabot | Weekly dependency and GitHub Actions update PRs |

Old generic `CI` and branch-mapped `CD` workflows were removed because they did not match the actual branch model and caused deployment runs to imply missing non-existent environment branches.

## Pull Request Rules

Protect `main` and require:

- Pull request before merge.
- `Required Quality Gate` from the `Pull Request Quality Gate` workflow.
- `Security Scanning` for code changes if GitHub code scanning is enabled.
- At least one approval when more than one maintainer is active.
- Linear history or squash merge for a clean release trail.
- No direct pushes to `main`, except emergency owner break-glass access.

## Deployment Flow

```text
feature/* or bugfix/*
        |
        v
Pull Request
        |
        v
Path-scoped quality gates + security scanning
        |
        v
Merge to protected main
        |
        v
Deploy Staging
        |
        v
Smoke tests and manual verification
        |
        v
Create tag vMAJOR.MINOR.PATCH
        |
        v
Deploy Production with environment approval
```

## Staging Deployment

`Deploy Staging` runs on every push to `main`.

Until hosting is selected, the deployment job is intentionally disabled unless the `staging` GitHub Environment has `DEPLOY_ENABLED=true`. Once enabled, the provider deployment hook must be replaced with real commands or a checked-in deploy script.

Required staging environment variables:

- `APP_URL`
- `API_BASE_URL`
- `DEPLOY_ENABLED`

Required staging environment secrets:

- `WEB_DEPLOY_TOKEN`
- `API_DEPLOY_TOKEN`
- `DATABASE_URL`
- `SUPABASE_JWT_SECRET`
- `GROQ_API_KEY` once the Groq layer is enabled

## Production Deployment

Production deployment is controlled by tags or manual dispatch:

- Preferred: create a tag like `v1.0.0`.
- Emergency/manual: run `Deploy Production`, provide `release_ref`, and type `deploy-production`.

Configure the `production` GitHub Environment with required reviewers before setting `DEPLOY_ENABLED=true`.

Required production environment variables and secrets are the same as staging, but with production values.

## Rollback Strategy

Use immutable release tags:

1. Identify the last known good tag.
2. Run `Deploy Production` manually.
3. Set `release_ref` to that tag.
4. Type `deploy-production`.
5. Verify `/health` and the web `APP_URL`.

Database rollback should be handled separately and carefully. Prefer backward-compatible migrations, expand-and-contract changes, and backups before destructive schema changes. Avoid automatic production downgrades unless the migration is explicitly designed and tested for rollback.

## Frontend and Backend Repository Strategy

Keep a monorepo with shared branches.

Reasons:

- The frontend and backend are product-coupled today.
- API compatibility is easier to review when client and server changes live in one PR.
- The repo is small enough that multi-repo overhead would outweigh the benefit.
- Path-scoped workflows provide independent CI without splitting Git history.
- Security boundaries are currently handled by secrets, environments, and least-privilege workflow permissions, not by repository separation.

Consider splitting repositories later only if separate teams own frontend/backend, release cadences diverge significantly, or access control requires different contributor populations.

## GitHub Permissions Needed

For `WajahatAliBasharat073/Meridian`, setup requires:

- Repository admin access.
- Permission to manage Actions workflows.
- Permission to create GitHub Environments.
- Permission to add environment variables and secrets.
- Permission to configure branch protection.
- Permission to configure code scanning and Dependabot alerts.
- Permission to create releases and tags.

## Manual Setup Commands

Create working branches only when needed:

```bash
git checkout main
git pull --ff-only
git checkout -b feature/my-change
```

Open a PR into `main`, then after staging passes:

```bash
git checkout main
git pull --ff-only
git tag -a v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

Emergency rollback:

```bash
git tag --list "v*.*.*"
```

Then run `Deploy Production` manually in GitHub Actions with `release_ref` set to the chosen previous tag.

## Hosting Still Needed

Provider-specific deployment is not wired yet. Choose:

- Web: Vercel is the natural fit for the Next.js app.
- API: Render, Railway, Fly.io, AWS App Runner/ECS, Azure Container Apps, or Google Cloud Run.
- Database/Auth: Supabase matches the current application design.

After choosing hosting, replace the provider hook steps in `deploy-staging.yml` and `deploy-production.yml` with real deploy commands and keep provider credentials in GitHub Environment secrets.
