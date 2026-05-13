# Family Voice Archive — End-to-End Implementation Plan

## Context

The project (`/Users/daniel.brito/Desktop/Family Story Vault/`) is greenfield — only `prd.md` and `CLAUDE.md` exist. The PRD (v1.0, May 2026) fully specifies a Telegram bot that captures parents' voice notes, transcribes them via Claude, stores audio + markdown in Google Drive (browsable in Obsidian), and indexes embeddings in Supabase pgvector for later RAG.

We are implementing it as a sequence of agent-executable phases. Each phase has a clear scope, deliverable, and verification step so an agent can be handed exactly one phase at a time without losing the thread.

**Decisions locked in via clarifying questions:**
- Embeddings: OpenAI `text-embedding-3-small` (1536-dim — matches the Supabase schema in PRD §10 exactly).
- Repo: `git init` + push to a new GitHub repo as part of Phase 0 (enables Render auto-deploy per PRD §14).
- Phase 1 ships with a `DRY_RUN` env flag to exercise the pipeline locally without burning quota.

---

## Phase 0 — Scaffolding, credentials, repo ✅ COMPLETE (2026-05-13)

**Goal:** Project skeleton compiles and starts (no-op), credentials are gathered, repo is on GitHub.

**Results**
- ✅ 24 files created — full directory tree per PRD §5, all stubs with docstrings
- ✅ `requirements.txt` — 12 packages including `openai>=1.0.0`
- ✅ `.env.example` — all 15 vars, no values
- ✅ `.gitignore` — excludes `.env`, `__pycache__/`, `*.pyc`, `*.json`, `.venv/`, `dryrun_output/`, `state/`
- ✅ `README.md` — setup instructions + DRY_RUN note
- ✅ `main.py` — verified: exits 0, logs `"Family Voice Archive started"`
- ✅ `pip install -r requirements.txt` — succeeded in fresh venv
- ✅ GitHub repo: https://github.com/danny031103/family-voice-archive (private)
- ✅ `.env` and service-account JSON NOT committed

**Pending before Phase 1**
- Add `MOM_CHAT_ID` and `DAD_CHAT_ID` to `.env` when available

**Deliverables**
- Directory tree exactly as PRD §5 — all module files exist as stubs with docstrings.
- `requirements.txt` per PRD §13, **plus** `openai>=1.0.0` (for embeddings).
- `.env.example` with every var from PRD §12 (no values).
- `.gitignore` excluding `.env`, `__pycache__`, the Google service-account JSON, `.venv/`.
- `README.md` linking to `prd.md` and `CLAUDE.md`.
- `main.py` boots: loads env, logs "started", exits cleanly (no bot yet).
- Use the `request-credentials` skill at the **start** of this phase to request every value in PRD §12.
- `git init`, initial commit, create GitHub repo, push to `main`.

**Critical files to create**
```
main.py, config.py, requirements.txt, .env.example, .gitignore, README.md
bot/{__init__.py,handlers.py,scheduler.py,commands.py}
processing/{__init__.py,claude.py,transcription.py,structurer.py,embeddings.py}
storage/{__init__.py,google_drive.py,obsidian.py,vector_db.py}
retrieval/{__init__.py,rag.py}
```

**Verification**
- `pip install -r requirements.txt` succeeds in a fresh venv.
- `python main.py` exits 0 with a "started" log line.
- `git log` shows initial commit; `gh repo view` resolves.

---

## Phase 1 — Core capture & processing pipeline ✅ COMPLETE (2026-05-13)

**Goal:** A real voice note sent to the bot produces an audio file + markdown note in Google Drive and an archivist notification. **No scheduler yet, no embeddings yet.**

**Results**
- ✅ `config.py` — all 16 env vars loaded as typed constants; `ALLOWED_CHAT_IDS` dict; `DRY_RUN` bool; `CLAUDE_MODEL` constant
- ✅ `processing/claude.py` — Anthropic client; `transcribe()` + `structure_transcript()` with tenacity 3× exponential backoff; JSON fence-stripping
- ✅ `processing/transcription.py` — reads audio bytes → `claude.transcribe()` → transcript; raises `TranscriptionError` on failure
- ✅ `processing/structurer.py` — calls `claude.structure_transcript()`, validates `title/themes/summary/folder` keys
- ✅ `storage/obsidian.py` — `make_slug`, `make_audio_filename`, `make_note_filename`, `format_note` per PRD §7 template
- ✅ `storage/google_drive.py` — service-account auth; `ensure_folder`; `upload_audio` → `_audio/<person>/`; `upload_note` → `<person>/<folder>/`; tenacity on uploads
- ✅ `bot/handlers.py` — full pipeline: allowlist check → download → transcribe → structure → format → DRY_RUN or Drive upload → confirm sender → notify archivist; unknown senders silently ignored; errors routed to archivist only
- ✅ `main.py` — `Application` polling with `VOICE` → `handle_voice` and `TEXT & ~COMMAND` → `handle_text`
- ✅ `DRY_RUN=true` writes to `./dryrun_output/<person>/`; logs what would be sent to Drive
- ✅ All imports verified clean: `python -c "import config; import bot.handlers; import processing.claude; import storage.google_drive; import storage.obsidian"` exits 0

**Pending verification (requires live Telegram + Drive)**
- Send a voice note with `DRY_RUN=true` → confirm `dryrun_output/` files with correct frontmatter
- Flip `DRY_RUN=false` → confirm files appear in Google Drive, archivist notified
- Text message → "Voice notes work best!" reply
- Unknown sender → silent ignore

**Deliverables**
- `bot/handlers.py`: voice-message handler — identifies sender by chat ID (allowlist from env), downloads `.ogg` from Telegram, ignores unknown senders silently, replies with "Got it, thank you ♥" on success, plain-text replies redirect to voice (PRD §11).
- `processing/claude.py`: single client wrapper with `tenacity` retry (3×, exponential backoff). Model: `claude-sonnet-4-20250514`.
- `processing/transcription.py`: audio bytes → base64 → Claude → raw transcript. Preserves speaker voice; inserts `[laughing]`, `[gets quiet]` stage directions per PRD §6.
- `processing/structurer.py`: transcript → JSON `{title, themes[], summary, folder}`. Claude picks the vault subfolder (e.g. `Mom/Childhood/`) from content.
- `storage/google_drive.py`: service-account auth from `GOOGLE_SERVICE_ACCOUNT_JSON`. Two functions: `upload_audio(path, person)` → `_audio/<person>/<filename>.ogg`; `upload_markdown(path, folder, content)` — auto-creates missing folders.
- `storage/obsidian.py`: renders markdown exactly per PRD §7 template (frontmatter + `![[file.ogg]]` embed + prompt + transcript).
- `main.py`: starts python-telegram-bot polling and registers the voice handler.
- **`DRY_RUN=true`** env flag: skip Drive uploads, write outputs to `./dryrun_output/`, log what *would* have been sent to Claude/Drive.
- Filenames: audio `YYYY-MM-DD-<person>-<slug>.ogg`, note `YYYY-MM-DD-<slug>.md`.
- Archivist notification on success: `"New story from <Person> saved! 🎵 <folder> > <title>"`.
- Error handling per PRD §15 (Claude failure → save raw audio flagged, notify archivist; Drive failure → retry then local fallback + notify).

**Verification**
- `DRY_RUN=true python main.py`, send a voice note to the bot from the archivist chat → markdown + audio appear in `./dryrun_output/` with correct frontmatter and embed syntax.
- Flip `DRY_RUN=false`, repeat → files appear in the Google Drive `Family Archive` folder, archivist receives the notification, Obsidian (pointed at the synced folder) plays the audio inline.
- Send a text message → bot replies with the "Voice notes work best!" message and does not process.
- Send from a chat ID not in the allowlist → bot silently ignores.

---

## Phase 2 — Prompt scheduler & basic commands

**Goal:** Bot autonomously prompts parents on cadence and supports archivist status commands.

**Deliverables**
- `config.py`: **prompt bank of 100+ prompts** across the categories in PRD §8 (childhood, family history, advice, about-archivist, funny, work, romance). Tone warm/conversational.
- `bot/scheduler.py`: APScheduler in the same process. One job per parent at their local `*_PROMPT_TIME` in `*_TIMEZONE`, firing every `PROMPT_CADENCE_DAYS`. Rotates through the prompt bank without repeats until exhausted (persist last-used index to a small JSON state file in Drive or local disk — pick local file, simpler).
- Nudge: if no voice note received 48h after a prompt, send one gentle follow-up. Never re-prompt twice.
- `bot/commands.py`:
  - `/status` — totals per person, last prompt sent, next scheduled.
  - `/history <name>` — last 10 recordings with titles + dates (read from a local index or Drive listing).
  - `/prompt <name>` — fires a prompt now, outside cadence.
  - `/add <name> <chat_id>` — appends to allowlist (writes to a local JSON state file; document that Render restart picks it up).
- Track sent prompts and pending responses in a small JSON state file (`state/scheduler_state.json`).

**Verification**
- Set `MOM_PROMPT_TIME` to ~2 minutes in the future → prompt arrives on Mom's Telegram at the right time in the right timezone.
- `/status` returns sensible counts; `/history Mom` lists recent notes.
- `/prompt Dad` fires immediately.
- Simulate "no response in 48h" by shortening the nudge interval in a debug env var → nudge sent once, not twice.

---

## Phase 3 — Embeddings (Supabase pgvector)

**Goal:** Every new recording gets an OpenAI embedding stored in Supabase, and historical notes are back-swept on startup.

**Deliverables**
- Provide the SQL from PRD §10 in `db/schema.sql`; document running it once in the Supabase SQL editor.
- `storage/vector_db.py`: Supabase client. `insert_recording(row)`, `find_unembedded()`, `mark_embedded(id)`.
- `processing/embeddings.py`: OpenAI `text-embedding-3-small` call (1536-dim). Input string: `title + " " + ",".join(themes) + " " + summary + " " + transcript` (per PRD §10).
- Wire into Phase 1 pipeline **after** the Drive upload succeeds. If embedding fails: log, mark note unembedded in `state/unembedded.json`, continue (PRD §15).
- On `main.py` startup, sweep `state/unembedded.json` and retry. Also detect rows in Supabase with `embedding IS NULL` and refill.
- All metadata stored alongside vector: person, title, date, themes, file paths.

**Verification**
- Send a voice note → row appears in Supabase `recordings` with non-null `embedding` and all metadata populated.
- Break the OpenAI key intentionally → note still saved, row written without embedding, `unembedded.json` records it, archivist notified.
- Restore key, restart bot → sweep picks it up and back-fills the embedding.

---

## Phase 4 — RAG `/ask` query

**Goal:** Archivist can ask natural-language questions over the archive in Telegram.

**Deliverables**
- `retrieval/rag.py`:
  1. Embed the question with the same OpenAI model.
  2. Supabase `match` query — top 5 by cosine similarity (requires `vector_cosine_ops` index on `embedding`; include in `db/schema.sql`).
  3. Build the Claude prompt verbatim from PRD §10 with the retrieved transcripts substituted.
  4. Generate answer, return alongside citation list (titles + dates + Obsidian paths).
- `bot/commands.py`: `/ask <question>` handler. Restricted to the archivist chat ID. Sends "Searching…" placeholder, edits with the result.
- Telegram reply format: warm answer paragraph + a bullet list of source recordings (title — date — folder path).

**Verification**
- Seed the archive with ≥5 real notes covering different themes.
- `/ask what did Mom say about her childhood?` returns an answer that quotes only retrieved notes and cites them.
- `/ask` with a topic absent from the archive → answer honestly says it doesn't have that info (per the PRD prompt).
- `/ask` from a non-archivist chat ID → ignored.

---

## Phase 5 — Render deployment & smoke test

**Goal:** Bot runs 24/7 on Render free tier, archivist's machine can be off.

**Deliverables**
- Render **Background Worker** (not Web Service) wired to the GitHub `main` branch.
- Build: `pip install -r requirements.txt`. Start: `python main.py`.
- All env vars from PRD §12 set in the Render dashboard.
- Google Drive desktop app installed on the archivist's Mac, syncing `Family Archive/` to a local path.
- Obsidian vault pointed at that local path; verify `.ogg` plays inline.
- README updated with: deploy steps, how to add a new family member, how to run locally with `DRY_RUN`.

**Verification**
- Push a trivial commit → Render auto-deploys, worker logs show "started".
- Send a voice note with the archivist's machine **off** → next time the Mac wakes, Drive syncs and the note appears in Obsidian with audio playable.
- `/status` from Telegram returns live data from the Render-hosted process.

---

## Out of scope (per PRD §17)

Photo support, annual summary, web view, birthday prompts, transcript corrections. Do not preemptively scaffold these.

## Cross-cutting rules

- All external API calls wrapped in `tenacity` exponential backoff.
- Parents never see errors — every failure path notifies the archivist's Telegram chat only.
- Unknown senders silently ignored, no reply.
- Never commit `.env` or the Google service-account JSON.
- Keep modules thin and aligned to the table in `CLAUDE.md` — no cross-module leakage.
