# Release Engineering Setup

This repo is configured with these GitHub Actions workflows:

- `Build & Quality Checks`: validates API, web, and local infrastructure config.
- `Release & Deployment`: promotes a validated build into the selected environment.

The deployment workflow supports these environments:

- `dev-sandbox`
- `staging`
- `qa`
- `uat`
- `production`

## Branch and Release Flow

| Source | Environment |
| --- | --- |
| `develop` | `dev-sandbox` |
| `staging` | `staging` |
| `qa` | `qa` |
| `uat` | `uat` |
| `main` | `production` |
| `v*.*.*` tag | `production` |
| Manual `workflow_dispatch` | selected environment |

Production manual deploys require `confirm_production=deploy-production`.

## What Is Active Now

- Pull requests and protected branches run API lint, typecheck, tests, web lint, web build, and Docker Compose validation.
- `Release & Deployment` runs the same quality gate before deployment.
- The deploy job validates required environment variables and secrets.
- Provider-specific deployment commands are intentionally isolated in `.github/workflows/cd.yml` until hosting is chosen; enabling deploys before replacing that hook will fail on purpose.
- Commit `web/` with these workflows, because CI now builds the Next.js app.

## Required GitHub Permissions

For the `wajahatalibasharat073` GitHub account or organization, the person wiring this up needs:

- Admin access to the repository.
- Permission to create and edit GitHub Actions workflows.
- Permission to create GitHub Environments.
- Permission to add repository and environment secrets/variables.
- Permission to configure branch protection rules.
- Permission to approve production deployments, if using required reviewers.

If I am doing it directly through a GitHub connection, grant access only to this repository and allow workflow, environment, secret, and deployment management.

## Recommended Environment Protection

| Environment | Reviewers | Branch restrictions |
| --- | --- | --- |
| `dev-sandbox` | optional | `develop` |
| `staging` | optional | `staging` |
| `qa` | QA owner | `qa` |
| `uat` | product/business owner | `uat` |
| `production` | owner/admin required | `main`, tags `v*.*.*` |

Protect `main` with required PR review and required CI status checks.

## Required Environment Variables

Add these as GitHub Environment variables for each environment:

- `APP_URL`: public web app URL for that environment.
- `API_BASE_URL`: public API URL for that environment.
- `DEPLOY_ENABLED`: set to `false` until provider-specific deploy commands are added, then `true`.

## Required Environment Secrets

Add these as GitHub Environment secrets for each environment:

- `WEB_DEPLOY_TOKEN`: deploy token for the selected web host.
- `API_DEPLOY_TOKEN`: deploy token for the selected API host.
- `DATABASE_URL`: deployed Postgres/Supabase connection string.
- `SUPABASE_JWT_SECRET`: JWT verification secret for deployed API auth.
- `GROQ_API_KEY`: required once the Groq layer is enabled.

Provider-specific setups may add more secrets, for example Vercel project/org IDs, AWS role ARN, Render service IDs, Railway project IDs, or Fly tokens.

## Hosting Choice Still Needed

Before CD can deploy real infrastructure, choose where each piece should run:

- Web: Vercel is the natural fit for Next.js.
- API: Render, Railway, Fly.io, AWS ECS/App Runner, Azure Container Apps, or Google Cloud Run all work.
- Database/Auth: Supabase matches the current design notes.

Once those are chosen, replace the `Deployment provider hook` step in `.github/workflows/cd.yml` with the exact deploy commands and keep all credentials in GitHub Environment secrets.
