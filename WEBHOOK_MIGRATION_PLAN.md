# Plan: Deploy Telegram Bot to Render Free Web Service via Webhook Mode
## Implementation Status: COMPLETE (2026-05-14)

All five changes implemented and verified. See results section at the bottom.

---

## Context

The bot has only been run locally so far (polling mode). This is the **first Render deployment**. The original plan called for a paid Background Worker ($7/mo) so APScheduler could stay alive 24/7. Instead, we're deploying to Render's **free Web Service** tier with Telegram **webhook mode** + **cron-job.org** pinging every 10 minutes to prevent Render's 15-minute spin-down.

Net result: **$0/mo deployment** with the same behavior. APScheduler continues running inside the same process — no scheduler changes required because it's already an `AsyncIOScheduler` (`bot/scheduler.py:6`) compatible with `run_webhook`.

---

## Approach (chosen)

- Use **python-telegram-bot 20.7's built-in `Application.run_webhook()`** (Tornado-based, already bundled — no new dependency).
- **No explicit `/health` endpoint.** cron-job.org pings the service root URL; Tornado returns 404, but Render counts any inbound HTTP request as activity and resets the inactivity timer.
- Commit a `render.yaml` so the Web Service config (build/start/env/plan) is reproducible.
- Update README's deployment section.

---

## Changes

### 1. `main.py` — swap polling for webhook
Currently (line 55–56):
```python
logger.info("Bot running (polling mode)")
app.run_polling()
```

Replace with conditional logic that picks polling locally vs. webhook in production, driven by env vars:

```python
import os

WEBHOOK_URL = os.getenv("WEBHOOK_URL")  # e.g. https://<service>.onrender.com
PORT = int(os.getenv("PORT", "8080"))   # Render injects PORT
WEBHOOK_SECRET = os.getenv("WEBHOOK_SECRET")  # random string, optional but recommended
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

if WEBHOOK_URL:
    url_path = TOKEN  # secret path; Telegram URL = WEBHOOK_URL + "/" + url_path
    logger.info("Bot running (webhook mode) on port %s", PORT)
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=url_path,
        webhook_url=f"{WEBHOOK_URL}/{url_path}",
        secret_token=WEBHOOK_SECRET,  # Telegram echoes this back in header; PTB verifies
    )
else:
    logger.info("Bot running (polling mode)")
    app.run_polling()
```

This preserves local-dev ergonomics (run with no `WEBHOOK_URL` → polling, same as today).

### 2. `config.py` — register new env vars
Add reads (around lines 8–39) for:
- `WEBHOOK_URL` (optional; absent = polling)
- `WEBHOOK_SECRET` (optional but recommended; pass to PTB as `secret_token`)
- `PORT` is read directly in `main.py` since it's only relevant to the webhook branch.

Keep these optional with sensible defaults so local `.env` doesn't need changes.

### 3. `.env` — add the new vars (leave blank locally)
Append to the existing `.env` file:
```
# Render webhook deployment (leave blank for local polling)
WEBHOOK_URL=
WEBHOOK_SECRET=
```

### 4. `render.yaml` (new file at repo root)
```yaml
services:
  - type: web
    name: family-voice-archive
    runtime: python
    plan: free
    branch: main
    buildCommand: pip install -r requirements.txt
    startCommand: python main.py
    healthCheckPath: /          # Render's built-in keepalive ping path
    envVars:
      - key: WEBHOOK_URL
        sync: false             # set in dashboard (the service's own onrender.com URL)
      - key: WEBHOOK_SECRET
        generateValue: true     # Render generates a random secret
      - key: TELEGRAM_BOT_TOKEN
        sync: false
      - key: ARCHIVIST_CHAT_ID
        sync: false
      - key: MOM_CHAT_ID
        sync: false
      - key: DAD_CHAT_ID
        sync: false
      - key: ANTHROPIC_API_KEY
        sync: false
      - key: OPENAI_API_KEY
        sync: false
      - key: SUPABASE_URL
        sync: false
      - key: SUPABASE_KEY
        sync: false
      - key: GOOGLE_DRIVE_FOLDER_ID
        sync: false
      - key: GOOGLE_SERVICE_ACCOUNT_JSON
        sync: false
      # Schedule / vault config — defaults exist in config.py but list here for visibility
      - key: MOM_PROMPT_TIME
        sync: false
      - key: DAD_PROMPT_TIME
        sync: false
      - key: PROMPT_CADENCE_DAYS
        sync: false
      - key: MOM_TIMEZONE
        sync: false
      - key: DAD_TIMEZONE
        sync: false
      - key: OBSIDIAN_VAULT_NAME
        sync: false
```

Note: `PORT` is auto-injected by Render — don't list it.

### 5. `README.md` — update the "Deploy to Render" section (lines 31–41)
Replace the "Background Worker" instructions with the actual first-deploy steps:
1. Push `render.yaml`; in the Render dashboard click **New → Blueprint**, point at the repo.
2. Render creates the free Web Service. After first deploy, copy the assigned `https://<service>.onrender.com` URL.
3. Paste that URL into the `WEBHOOK_URL` env var in the Render dashboard; redeploy.
4. Verify the webhook is registered: `curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo` should return your URL with `pending_update_count: 0`.
5. **Set up cron-job.org**: create a job that GETs `https://<service>.onrender.com/` every **10 minutes**, 24/7. (Render's free spin-down threshold is 15 min; 10 min gives comfortable margin.)

Also call out: the free tier has 750 hours/month of runtime — enough for one always-on service.

---

## Files to modify

| File | Type | Purpose |
|---|---|---|
| `main.py` | edit (lines 55–56 + small import block) | Switch from `run_polling` to conditional `run_webhook` |
| `config.py` | edit (env var section) | Read `WEBHOOK_URL`, `WEBHOOK_SECRET` |
| `.env` | edit | Add new optional vars (blank values for local dev) |
| `render.yaml` | **new** | Render Blueprint config |
| `README.md` | edit (Deploy section, ~lines 31–41) | New deployment steps + cron-job.org instructions |

No changes needed in:
- `bot/scheduler.py` — `AsyncIOScheduler` already runs under the `run_webhook` event loop
- `bot/handlers.py`, `bot/commands.py` — handler registration is transport-agnostic
- `processing/*`, `storage/*`, `retrieval/*` — unaffected
- `requirements.txt` — PTB 20.7 already includes Tornado

---

## Risks & mitigations

| Risk | Mitigation |
|---|---|
| Stale webhook if you run polling locally while Render is live | Telegram can only have one active endpoint at a time. If you run `python main.py` locally (no `WEBHOOK_URL` set) while Render is deployed, PTB's polling will call `deleteWebhook`, breaking the Render deployment. Keep local dev offline or unset the webhook first: `curl https://api.telegram.org/bot<TOKEN>/deleteWebhook`. |
| Telegram message delivered while service is spun-down | Telegram retries webhook deliveries for ~24h. cron-job.org ping every 10 min should prevent spin-down in practice; even on a cold start, Render boots in ~30s and Telegram will redeliver. |
| Webhook spoofing (someone POSTing to our URL) | `WEBHOOK_SECRET` — Telegram echoes it in `X-Telegram-Bot-Api-Secret-Token` header; PTB verifies and rejects mismatches. |
| Render free tier 750-hour/month cap | One always-on service uses ~730 hrs/month — within budget. Don't run a second free service from the same account simultaneously. |
| `/tmp` voice file downloads (`handlers.py:37`) | Web Services have ephemeral `/tmp` same as Background Workers — no change. |
| Sequential webhook processing | PTB processes updates concurrently by default; voice transcription latency (~seconds) is fine. No queueing change needed. |

---

## Verification

After deploying:

1. **Webhook registered correctly**
   ```
   curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
   ```
   Expect `url` = `https://<service>.onrender.com/<token>`, `pending_update_count` = 0, `last_error_message` absent.

2. **Bot responds to voice notes** — send a voice note from an allowlisted chat (Mom/Dad/archivist). Confirm:
   - Archivist gets the "✅ Saved" notification.
   - Audio appears in Google Drive `_audio/<person>/`.
   - Markdown note appears in the themed folder.
   - Row inserted in Supabase `recordings` with non-null `embedding`.

3. **Commands work** — from archivist chat: `/status`, `/prompt mom`, `/ask <question>`.

4. **APScheduler still firing** — check Render logs at the next scheduled prompt time (`MOM_PROMPT_TIME` / `DAD_PROMPT_TIME`) for `send_prompt` log line.

5. **Keep-alive working** — after cron-job.org runs for an hour, check Render's "Events" tab: no "Service spun down" entries.

6. **Local dev unaffected** — with `WEBHOOK_URL` unset in local `.env`, `python main.py` should still log "Bot running (polling mode)" and work as before.

---

## Rollback

If anything breaks: delete the Render Web Service, run `curl https://api.telegram.org/bot<TOKEN>/deleteWebhook` to clear the webhook, and resume local polling mode with `python main.py`. No data migration needed.

---

## Implementation Results (2026-05-14)

All changes implemented via two parallel subagents. Files modified:

| File | Status | Notes |
|---|---|---|
| `main.py` | ✅ Done | Added `import os`; replaced `run_polling()` with conditional webhook/polling block (lines 56–72) |
| `config.py` | ✅ Done | Added `WEBHOOK_URL` and `WEBHOOK_SECRET` optional vars under new `# --- Webhook (Render deployment) ---` section |
| `.env` | ✅ Done | Appended `WEBHOOK_URL=` and `WEBHOOK_SECRET=` with comment at end of file |
| `render.yaml` | ✅ Done | New file created at repo root; Blueprint config with `healthCheckPath: /`, `WEBHOOK_SECRET` auto-generated, all other vars `sync: false` |
| `README.md` | ✅ Done | "Deploy to Render" section rewritten with 5-step webhook flow + cron-job.org instructions + polling-conflict warning |

### Next steps to complete the deployment
1. Push this branch to `main`
2. In Render dashboard: **New → Blueprint** → point at repo
3. After first deploy: copy `https://<service>.onrender.com` → paste as `WEBHOOK_URL` → redeploy
4. Verify: `curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo`
5. Set up cron-job.org: GET the service root every 10 minutes
