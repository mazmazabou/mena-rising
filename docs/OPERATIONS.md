# MENA Rising — Operations Runbook

Cold-start notes for whoever picks this up next. The weekly issue is fully automated; nobody needs to watch it. Open this when the pipeline breaks or a change is requested.

Last verified: **2026-10-27**, ahead of Issue #030 (week of November 2, 2026).

## How the weekly run works

`.github/workflows/weekly_brief.yml`, cron `0 6 * * 1` (Mondays 06:00 UTC), also runnable by hand (`gh workflow run weekly_brief.yml`). Steps, in order:

1. **Archive current brief** — `run_pipeline.py --archive-only` copies `public/data/latest_brief.json` to `public/data/archive/issue-NNN.json` and prepends `manifest.json`.
2. **Run pipeline** — `run_pipeline.py`: Phase 1 `collect_data.py` (6 sources → `pipeline/data_payload.json`), Phase 2 `generate_brief.py` (Claude → `latest_brief.json`). Issue number = previous + 1; `weekOf` = that Monday.
3. **Generate sitemap**, then **commit and push** as `chore: weekly brief update — Issue #NNN`. The push to `main` triggers the Vercel production deploy of mena-rising.com.
4. **Send newsletter** — `send_newsletter.py` creates and sends a Resend broadcast to the audience.
5. **Notify on failure** — `send_failure_alert.py` emails abouelelamazen@gmail.com with the run link.

Secrets (repo Actions secrets): `ANTHROPIC_API_KEY`, `FRED_API_KEY`, `FINNHUB_API_KEY`, `NEWS_API_KEY`, `RESEND_API_KEY`, `RESEND_AUDIENCE_ID`. Checkout uses the default `GITHUB_TOKEN`.

## Claude model

`CLAUDE_MODEL` in `pipeline/config.py` (currently `claude-sonnet-5-5`). The June–October 2026 outage (first failing run 2026-06-22; Issue #029 was the first to publish after it) was the old pinned model `claude-sonnet-4-20250514` being retired: the API returned `404 not_found_error` and Phase 2 failed every week. If generation suddenly 404s, check the model ID first, not the key.

Model constraints the call in `call_claude_with_retry()` already respects: no non-default `temperature`; thinking is on by default, so the text is joined from `type == "text"` blocks rather than read from `content[0]`. The `anthropic` SDK is pinned `>=0.80.0,<1.0.0` in `pipeline/requirements.txt` (1.x+ is a breaking major).

## Editorial rules (from Issue #030 on)

All in `pipeline/generate_brief.py`:

- `build_system_prompt()` — frames the brief as economics and business first.
- `build_user_prompt()` — the `EDITORIAL RULES` block:
  - **A.** Lead with a security story only if it escalated this week in a specific named way (new front, major oil move, policy change); otherwise lead with the biggest economy/business story.
  - **B.** `notableFlows[0]` is always the biggest non-security story (IPOs, central banks, megaprojects, sovereign funds, Gulf AI/tech deals).
  - **C.** A risk repeated from the previous issue must open its description with "Since last week:" and say what changed; a materially escalated risk must stay.
- `load_previous_brief()` / `format_previous_brief()` feed the previous issue into the prompt (read from `latest_brief.json` before it is overwritten).
- `check_repeated_risks()` logs a soft warning if a repeated risk lacks "Since last week:".

Supporting input: `fetch_news()` in `pipeline/collect_data.py` runs two NewsAPI queries — a general MENA one and a title-only business query (IPO, central bank, PIF, Mubadala, data center, AI, deal, megaproject…) — tagged by `category` so the prompt gets a separate "BUSINESS & MARKETS HEADLINES" section.

## Newsletter

- HTML: `build_html()` in `pipeline/send_newsletter.py` — table layout with inline styles for Outlook, ~14 KB (Gmail clips above 102 KB).
- Animated header: `public/email/masthead.gif`, loaded from `https://mena-rising.com/email/masthead.gif`. Frame 1 is the finished static design (Outlook shows only that). Regenerate with `python3 scripts/generate-email-gif.py` (Pillow). It must be deployed on mena-rising.com or the email shows a broken image.
- Unsubscribe link uses Resend's `{{{RESEND_UNSUBSCRIBE_URL}}}`, which Resend fills in **only for broadcasts**. For a one-off test send, replace it (e.g. with the site URL).
- Resend refuses a broadcast if the audience contains an `@example.com` contact. `api/subscribe.ts` and the Vite dev plugin in `vite.config.ts` now reject example.com signups. If a send fails with that error, delete the contact in the audience.
- Sending domain `mena-rising.com` is verified in Resend.

## Verification for Issue #030 (2026-10-27)

- Workflow state `active`; all six secrets present. Run 40418392355 (Oct 26) passed every step through commit/push with the CI secrets; only the send failed (example.com contact, since removed).
- Full rehearsal in a fresh clone of `main` at `77f4d5b` (archive → `run_pipeline.py` → sitemap): exit 0, 6/6 sources, 12/12 macro metrics, Issue #030 / November 2, 2026. GDELT returned 429 once and the built-in retry recovered.
- Editorial rules held: lead was a Gulf capital story (Apollo / Mubadala Capital, UAE money in an OpenAI round) where #029 led with Houthi attacks; `notableFlows[0]` non-security; both repeated risks opened "Since last week:".
- Email rendered from the rehearsed #030 brief (14.4 KB, GIF and unsubscribe placeholder present). Nothing was sent to subscribers.
- Audience: 3 contacts, 0 unsubscribed, no test/example domains.
- A test email in the new design was delivered to abouelelamazen@gmail.com on 2026-10-27 (Resend id `01a17e52-0d91-7e3b-9ae3-ce74e0a7ebeb`).

## When it breaks

1. `gh run list -R mazmazabou/mena-rising -w weekly_brief.yml -L 5`, then `gh run view <id> --log-failed`. Logs expire after 90 days (HTTP 410); step-level pass/fail is still available via `gh run view <id> --json jobs`.
2. Workflow shows `disabled_inactivity`: GitHub disables scheduled workflows after 60 days without repo activity. `gh workflow enable weekly_brief.yml -R mazmazabou/mena-rising`.
3. Phase 2 fails: check the model ID (above) and Anthropic credit before suspecting the key.
4. Send fails but the issue published: fix the cause, then send the existing draft broadcast from Resend, or rerun `python send_newsletter.py` (creates a new broadcast — don't do both).

### Rehearsing safely

`run_pipeline.py --dry-run` is **not** dry: it still archives and overwrites `latest_brief.json`. To rehearse, clone `main` into a temp dir, copy `pipeline/.env` in, and run the workflow steps there (`run_pipeline.py --archive-only`, `run_pipeline.py`, `node scripts/generate-sitemap.js`). That costs one Claude call and touches nothing live.

## Known non-blocking items

- Validation may warn `risks missing level: HIGH` — soft warning, exit 0, by design.
- Labor Signals "Tech sector postings" trend arrow can point the wrong way (pre-existing, cosmetic).
- Pre-existing lint errors in `src/components/ui/command.tsx` and `textarea.tsx` (shadcn files).
- Local dev: the repo lives in iCloud-synced `~/Documents`; evicted `node_modules` files make tsc/eslint/vite/vitest hang at ~0% CPU. Run `find node_modules -flags +dataless | wc -l` to confirm; work around by building from a copy outside `~/Documents` after `npm ci`.
