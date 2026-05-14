# Family Voice Archive

A Telegram bot that sends scheduled story prompts to family members, collects voice note responses, transcribes them via Claude AI, and saves audio + markdown notes to Google Drive for browsing in Obsidian.

Full specification: [prd.md](prd.md)

---

## Local setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Run the Supabase schema (first time only) — paste the contents of `db/schema.sql` into the Supabase SQL editor and run it.

3. Start the bot:
   ```bash
   python main.py
   ```

---

## DRY_RUN mode

Set `DRY_RUN=true` in `.env` to skip real uploads to Google Drive and Supabase during local testing. Output is written to `dryrun_output/` instead.

---

## Deploy to Render

The bot runs as a free **Web Service** on Render using Telegram webhook mode. A cron-job.org job pings the service every 10 minutes to prevent Render's 15-minute spin-down. Total cost: **$0/mo**.

### First deploy

1. Push `render.yaml` to `main`; in the Render dashboard click **New → Blueprint** and point it at the repo. Render creates the free Web Service automatically.
2. After the first deploy completes, copy the assigned URL: `https://<service>.onrender.com`
3. Paste that URL as the value of the `WEBHOOK_URL` env var in the Render dashboard, then redeploy.
4. Verify the webhook registered:
   ```
   curl https://api.telegram.org/bot<TOKEN>/getWebhookInfo
   ```
   Expect `url` = `https://<service>.onrender.com/<token>` and `pending_update_count: 0`.
5. **Set up cron-job.org**: create a job that GETs `https://<service>.onrender.com/` every **10 minutes**, 24/7.

For `GOOGLE_SERVICE_ACCOUNT_JSON`: paste the **entire contents** of the service account JSON file as the value (not a file path).

Auto-deploy is enabled — every push to `main` triggers a redeploy.

> **Warning**: do not run `python main.py` locally while Render is live. PTB polling calls `deleteWebhook` and breaks the deployment. To resume local dev, first run `curl https://api.telegram.org/bot<TOKEN>/deleteWebhook`.

---

## Adding a new family member

Use the `/add` bot command from your archivist Telegram chat:

```
/add Name ChatID
```

This writes to `state/allowlist.json` and takes effect after the next bot restart or Render redeploy.

---

## Obsidian setup

1. Install the [Google Drive desktop app](https://www.google.com/drive/download/) and sign in.
2. In Obsidian: **Open folder as vault** → select the locally synced `Family Archive` folder.
3. Audio files play inline via `![[filename.ogg]]` — no plugin needed.
4. Recommended plugins: **Dataview** (query by tag/date), **Calendar** (timeline view).

---

## Project structure

```
main.py                   Entry point — starts polling + APScheduler
config.py                 Env vars, constants, prompt bank (100+ prompts)
bot/
  handlers.py             Telegram message handlers (voice note pipeline)
  scheduler.py            APScheduler prompt cadence + nudge logic
  commands.py             /ask, /status, /history, /prompt, /add
processing/
  claude.py               All Claude API calls
  transcription.py        Audio → raw transcript
  structurer.py           Transcript → structured JSON (title, themes, folder)
  embeddings.py           Generate OpenAI embeddings and store in Supabase
storage/
  google_drive.py         Upload audio + markdown to Drive
  obsidian.py             Format Obsidian markdown notes
  vector_db.py            Supabase pgvector read/write
retrieval/
  rag.py                  Semantic search + Claude answer generation (/ask)
db/
  schema.sql              Supabase table + RPC function (run once)
state/                    Local JSON state files (gitignored)
```
