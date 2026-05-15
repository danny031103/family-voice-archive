# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project

Family Voice Archive — a Telegram bot that sends scheduled story prompts to family members, collects voice note responses, transcribes them via OpenAI Whisper, and saves audio + markdown notes to Google Drive for browsing in Obsidian.

Full specification: `prd.md`

---

## Running the bot

```bash
# Install dependencies
pip install -r requirements.txt

# Run locally (polling mode — no webhook or tunnel needed)
python main.py
```

Copy `.env.example` to `.env` and fill in all values before running. See `prd.md` section 12 for how to obtain each credential.

---

## Architecture

The pipeline runs on every incoming voice note:

```
Telegram voice note → download audio → Whisper transcription → Claude structuring
→ Google Drive (audio file) → Google Drive (markdown note) → Supabase embedding
→ Archivist notification
```

The bot runs on Render as a **free Web Service** using Telegram **webhook mode**. A cron-job.org job pings the service root every 10 minutes to prevent Render's 15-minute spin-down. APScheduler runs inside the same process for prompt scheduling — no changes needed from polling mode.

Local dev uses polling mode (no `WEBHOOK_URL` set). **Do not run locally while Render is live** — PTB's polling will call `deleteWebhook` and break the deployment.

### Module responsibilities

| Module | Purpose |
|---|---|
| `main.py` | Entry point — starts Telegram polling + APScheduler |
| `config.py` | All env vars, constants, and the 100-prompt bank |
| `bot/handlers.py` | Telegram message handlers (voice note reception) |
| `bot/scheduler.py` | APScheduler cadence — prompts every 2 days per parent, nudge if no reply in 48h |
| `bot/commands.py` | `/ask`, `/status`, `/history`, `/prompt`, `/add` |
| `processing/claude.py` | All Claude API calls |
| `processing/transcription.py` | Audio file path → raw transcript via Whisper |
| `processing/structurer.py` | Raw transcript → structured JSON (title, themes, summary, stage directions) |
| `processing/embeddings.py` | Generate embeddings and write to Supabase pgvector |
| `storage/google_drive.py` | Upload audio `.ogg` and markdown `.md` to Drive |
| `storage/obsidian.py` | Format markdown notes (frontmatter + `![[audio.ogg]]` embed + transcript) |
| `storage/vector_db.py` | Supabase pgvector read/write for the `recordings` table |
| `retrieval/rag.py` | Phase 4 — semantic search + Claude answer generation |

### Claude API usage

- Model: `claude-sonnet-4-20250514`
- Transcription: OpenAI Whisper (`whisper-1`) via `openai` SDK — Claude's document content block does not support `.ogg` audio and raises `BadRequestError`
- Structuring: Claude extracts title, themes (auto-generates vault folder), summary (`[laughing]`-style stage directions are not currently added — Whisper returns plain text)
- Embeddings: `text-embedding-3-small` via OpenAI (decide on cost)
- All Claude calls live in `processing/claude.py`; Whisper call lives in `transcribe()` in the same file

### Google Drive / Obsidian layout

```
Family Archive/          ← Drive root = Obsidian vault root
├── Mom/
│   ├── Childhood/
│   └── ...              ← folders auto-created by Claude from content
├── Dad/
│   └── ...
├── _audio/mom/          ← all .ogg files
├── _audio/dad/
└── _index/              ← auto-generated overview notes
```

Audio filename format: `YYYY-MM-DD-person-slug.ogg`
Note filename format: `YYYY-MM-DD-slug.md`

Obsidian embeds audio inline via `![[filename.ogg]]` — no plugin required.

### Supabase schema

```sql
create table recordings (
  id uuid primary key default gen_random_uuid(),
  person text not null,
  title text not null,
  date date not null,
  prompt text,
  themes text[],
  summary text,
  transcript text not null,
  audio_drive_path text,
  obsidian_note_path text,
  embedding vector(1536),
  created_at timestamptz default now()
);
```

Embedding input: `title + " " + themes joined + " " + summary + " " + transcript`

### Error handling

All external API calls use `tenacity` with exponential backoff. Key rules:
- Claude failures: retry 3×, then save raw audio to Drive flagged for manual transcription, notify archivist
- Supabase failures: log and continue — mark note unembedded, sweep on next restart
- Parents never see error messages — errors go to archivist's Telegram chat only
- Unknown senders (chat ID not in allowlist): silently ignored

### Build order

Phase 1 (core pipeline) → Phase 2 (scheduler + prompt bank) → Phase 3 (embeddings) → Phase 4 (RAG `/ask`)

Embeddings must be wired in during Phase 1 pipeline to avoid backfill later — even if Phase 4 is months away.
