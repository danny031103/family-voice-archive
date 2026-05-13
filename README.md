# Family Voice Archive

A Telegram bot that sends scheduled story prompts to family members, collects voice note responses, transcribes them via Claude AI, and saves audio + markdown notes to Google Drive for browsing in Obsidian.

Full specification: [prd.md](prd.md)

---

## Setup

1. Copy `.env.example` to `.env` and fill in all credential values:
   ```bash
   cp .env.example .env
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run the bot:
   ```bash
   python main.py
   ```

---

## DRY_RUN mode

Set `DRY_RUN=true` in `.env` to skip real uploads to Google Drive and Supabase during local testing. Output will be written to `dryrun_output/` instead.

---

## Project structure

```
main.py                   Entry point
config.py                 Env vars, constants, prompt bank
bot/
  handlers.py             Telegram message handlers
  scheduler.py            APScheduler prompt cadence
  commands.py             /ask, /status, /history, /prompt, /add
processing/
  claude.py               All Claude API calls
  transcription.py        Audio → transcript
  structurer.py           Transcript → structured JSON
  embeddings.py           Generate and store embeddings
storage/
  google_drive.py         Upload audio + markdown to Drive
  obsidian.py             Format Obsidian markdown notes
  vector_db.py            Supabase pgvector read/write
retrieval/
  rag.py                  Semantic search + Claude answer generation
```
