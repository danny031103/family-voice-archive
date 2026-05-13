# Family Voice Archive — Product Requirements Document
**Version 1.0 · May 2026**

---

## Prompt for Claude Code

Build Phase 1 of the Family Voice Archive per this PRD. Start with the project structure, then the Telegram bot handler, then the Claude transcription pipeline, then Google Drive upload, then the Obsidian note formatter.

---

## 1. Project Overview

Family Voice Archive is a Telegram bot system that sends scheduled story prompts to family members (initially parents), collects their voice note responses, transcribes them using Claude AI, and stores both the original audio and the cleaned transcript in an organized, searchable archive.

The archive lives in Google Drive (as the storage backbone) and surfaces in Obsidian (for visual browsing, graph view, and inline audio playback). A RAG (Retrieval Augmented Generation) semantic search layer is built in from day one so the archive can be queried conversationally later.

**Core philosophy:** Low friction for the parents (they just reply to a Telegram message), rich experience for the archivist (you), and permanent ownership of everything including the actual voice recordings.

---

## 2. Goals & Non-Goals

### Goals
- Capture parents' stories, advice, memories, and wisdom in their own voice
- Preserve the actual audio recording of every response — not just the text
- Automatically transcribe and clean up voice notes without changing the speaker's words
- Organize everything into a browsable, searchable archive in Obsidian
- Make the experience effortless for parents — they just reply to a Telegram message
- Store embeddings from day one so semantic search can be added later with no backfill
- Keep all data permanently owned and locally stored — not locked in a third-party service

### Non-Goals
- Not a social or sharing platform — this is a private family archive
- Not a replacement for real conversations — it supplements them
- Not building a mobile app — Telegram handles the interface
- Not auto-publishing or sharing recordings without explicit action

---

## 3. Users

| User | Description |
|---|---|
| Archivist (you) | Sets up and runs the system. Receives notifications. Browses the archive in Obsidian. Will eventually use the /ask RAG query feature. |
| Parents | Receive scheduled prompts via Telegram. Reply with voice notes. No technical knowledge required beyond knowing how to send a voice message in Telegram. |
| Future users | Siblings or other family members could be added as additional respondents with their own Telegram accounts and prompt schedules. |

---

## 4. System Architecture

### Architecture Overview

```
CAPTURE   →  Telegram bot receives voice notes from parents on a scheduled prompt cadence or on-demand
PROCESS   →  Claude API transcribes audio, cleans transcript, extracts metadata, generates embedding
STORE     →  Audio file + markdown note saved to Google Drive. Embedding stored in Supabase pgvector.
RETRIEVE  →  Obsidian reads from Google Drive sync folder for visual browsing. Bot handles /ask via RAG.
```

### Tech Stack

| Piece | Tool |
|---|---|
| Language | Python 3.11+ |
| Bot framework | python-telegram-bot v20+ (polling mode — no webhook, no web server needed) |
| AI processing | Anthropic Claude API — claude-sonnet-4-20250514 |
| Voice transcription | Claude API (audio sent as base64 — no Whisper needed) |
| Embeddings | Claude API or text-embedding-3-small via OpenAI (decide based on cost) |
| Vector database | Supabase pgvector (free tier) |
| Primary storage | Google Drive (audio files + markdown notes) |
| Visual layer | Obsidian desktop + mobile, vault pointed at Google Drive sync folder |
| Scheduler | APScheduler (runs inside the bot process — no separate cron needed) |
| Deployment | Render background worker — free tier, no spin-down for background workers |
| Google Drive sync | Google Drive desktop app syncs to local folder that Obsidian vault points at |

---

## 5. Project Structure

```
family-voice-archive/
├── main.py                    # Entry point — starts bot polling + scheduler
├── config.py                  # All env vars, constants, prompt bank
├── requirements.txt
├── .env                       # Never committed to git
├── .env.example               # Committed — shows all required vars with no values
│
├── bot/
│   ├── handlers.py            # Telegram message handlers
│   ├── scheduler.py           # APScheduler prompt cadence logic
│   └── commands.py            # /ask, /status, /history commands
│
├── processing/
│   ├── claude.py              # All Claude API calls
│   ├── transcription.py       # Voice memo → raw transcript
│   ├── structurer.py          # Raw transcript → structured note JSON
│   └── embeddings.py          # Generate + store embeddings
│
├── storage/
│   ├── google_drive.py        # Upload audio + markdown to Drive
│   ├── obsidian.py            # Format and write markdown notes
│   └── vector_db.py           # Supabase pgvector read/write
│
└── retrieval/
    └── rag.py                 # Semantic search + answer generation
```

---

## 6. Core Capture & Processing Flow

This pipeline runs every time a parent sends a voice note to the bot:

1. Telegram delivers voice message to bot handler
2. Bot identifies sender (Mom or Dad) from Telegram chat ID
3. Bot downloads raw audio file from Telegram servers
4. Audio converted to base64, sent to Claude API for transcription
5. Claude cleans transcript: natural language cleanup, preserves speaker's voice and phrasing, adds stage directions for tone (e.g. `[laughing]`, `[gets quiet]`)
6. Claude generates structured metadata: title, theme tags, one-line summary, related themes
7. Audio file saved to Google Drive with clean filename: `YYYY-MM-DD-person-slug.ogg`
8. Markdown note written to Google Drive with frontmatter, prompt, transcript, and audio embed link
9. Embedding generated from transcript + metadata, stored in Supabase pgvector
10. Bot sends archivist a notification: `"New story from Mom saved! 🎵 Childhood > Playing in the Street"`

---

## 7. Obsidian Note Format

Every voice note produces exactly one markdown file. The format is designed to render beautifully in Obsidian with the audio player inline.

### Markdown file template

```markdown
---
title: Playing in the Street After School
person: Mom
date: 2026-05-12
prompt: "What is a memory from your childhood that still makes you laugh?"
theme: [childhood, funny, neighborhood, friends]
summary: Mom recalls racing homemade go-karts down the street with neighborhood kids and crashing into Mrs. Henderson's garden.
audio: _audio/mom/2026-05-12-mom-childhood-memory.ogg
duration: 2m 34s
related: [[Growing Up]], [[Grandma and Grandpa]], [[Funny Stories]]
---

## Prompt
"What is a memory from your childhood that still makes you laugh?"

## Voice Recording
![[2026-05-12-mom-childhood-memory.ogg]]

## Transcript
Oh god, okay [laughing]. So when I was maybe eight or nine, the boys on our street built these go-karts out of wood and old pram wheels, right? And they would race them down Maple Street which had a hill at the end...

[gets quieter]

...Mrs. Henderson never actually got that angry. I think she secretly loved it.
```

The `![[filename.ogg]]` syntax is Obsidian's native audio embed — it renders as an inline playable audio player directly in the note.

### Vault folder structure

```
Family Archive/              ← Obsidian vault root (= Google Drive sync folder)
│
├── Mom/
│   ├── Childhood/
│   │   ├── 2026-05-12-playing-in-the-street.md
│   │   └── 2026-05-19-first-day-of-school.md
│   ├── Advice/
│   ├── Family History/
│   ├── Funny Stories/
│   └── About Me (the archivist)/
│
├── Dad/
│   ├── Childhood/
│   ├── Work & Career/
│   ├── Advice/
│   └── Funny Stories/
│
├── _audio/                  ← All .ogg audio files live here
│   ├── mom/
│   └── dad/
│
└── _index/                  ← Auto-generated index notes
    ├── Mom Overview.md      ← All Mom stories linked by theme
    └── Dad Overview.md
```

Topics and subtopics are auto-generated by Claude based on content — vault structure grows organically over time. Claude should create the folder if it doesn't exist before writing the note.

---

## 8. Prompt System

### Scheduling

| Setting | Value |
|---|---|
| Default cadence | Every 2 days per parent |
| Send time | Configurable per parent via env var (e.g. `10:00` their local time) |
| Scheduler | APScheduler — runs inside main.py process |
| Missed response | If no response after 48 hours, bot sends one gentle nudge. Does not re-prompt endlessly. |
| On-demand | Parents can message the bot anytime unprompted — any voice note received is processed through the full pipeline |

### Prompt bank

Stored in `config.py` as a list. Prompts rotate and never repeat until the full bank is exhausted. Generate at least 100 prompts total across these categories:

**Childhood memories**
- "What is a memory from your childhood that still makes you laugh?"
- "What did you and your friends do for fun growing up?"
- "What was your home like when you were little?"
- "What was your favourite thing to do after school?"
- "What was your neighbourhood like growing up?"

**Family history**
- "Tell me about your parents — what were they like?"
- "What is something your parents taught you that you have never forgotten?"
- "Where did our family originally come from?"
- "What was your relationship with your siblings like?"
- "What is a family tradition you remember from childhood?"

**Advice & wisdom**
- "What is the best piece of advice anyone ever gave you?"
- "What do you know now that you wish you had known at 25?"
- "What is something you would tell your younger self?"
- "What is the most important lesson life has taught you?"
- "What do you think makes a good life?"

**About the archivist**
- "What was I like as a baby?"
- "Tell me about the day I was born"
- "What is your favourite memory of us together?"
- "What did you hope for me when I was born?"
- "What is something about me that always made you proud?"

**Funny stories**
- "What is the funniest thing that ever happened to you?"
- "Tell me about a time something went completely wrong but you laughed about it later"
- "What is the most embarrassing thing that ever happened to you?"

**Work & career**
- "What was your first job like?"
- "What is something memorable that happened at work over the years?"
- "What did you want to be when you grew up?"

**Romance**
- "How did you and [spouse] first meet?"
- "What was your first date like?"
- "What made you know [spouse] was the one?"

Claude Code should generate additional prompts to reach 100 total. Keep the tone warm and conversational, not clinical.

---

## 9. Google Drive & Obsidian Setup

### How the sync works

The bot writes all files to Google Drive via the Google Drive API. The Google Drive desktop app syncs this folder to a local directory. Obsidian vault is pointed at that local directory.

This means:
- Bot runs on Render — your computer does not need to be on for the bot to capture recordings
- Files accumulate in Google Drive automatically while you are away
- Whenever you open your computer, Google Drive syncs and Obsidian sees all new notes
- Audio files play inline in Obsidian via the `![[filename.ogg]]` embed syntax

### Obsidian configuration

| Setting | Detail |
|---|---|
| Vault location | Point Obsidian vault at the locally synced Google Drive folder |
| Audio playback | Obsidian natively plays .ogg files — no plugin needed |
| Graph view | Enable in View menu — nodes appear automatically as notes link via `[[wikilinks]]` |
| Recommended plugins | Dataview (query notes by tag/date), Calendar (timeline view) |
| Mobile | Obsidian mobile app can also point at the Google Drive sync for mobile browsing |

---

## 10. RAG Semantic Search Layer

### Why embed from day one

Even though the `/ask` query feature is Phase 4, embeddings must be stored from day one. Adding RAG later without embeddings means going back and re-processing every note that already exists. The embedding step added now is ~20 lines of code in the pipeline.

### Embedding storage schema (Supabase)

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

### What gets embedded

Concatenate for embedding: `title + " " + themes joined + " " + summary + " " + transcript`

### /ask query flow (Phase 4 — build when ready)

1. Archivist sends: `/ask what did mom say about her childhood?`
2. Bot embeds the question using the same embedding model
3. Supabase returns top 5 most semantically similar recordings
4. Claude generates an answer using only those recordings as context
5. Bot replies with answer and lists which recordings it drew from
6. Archivist can open those notes in Obsidian for full recording + transcript

### Claude prompt for RAG answers

```
You are answering a question using only the following voice recordings
from a personal family archive. The recordings are transcripts of a
family member speaking naturally.

Answer in a warm, personal tone. Refer to the speaker by name.
Always cite which recording(s) you are drawing from at the end of your answer.
If the recordings do not contain enough information to answer,
say so honestly. Never invent or assume details not present in the transcripts.

Recordings:
{retrieved_notes}

Question: {question}
```

---

## 11. Bot Commands & Interactions

### Commands available to archivist

| Command | Function |
|---|---|
| `/ask [question]` | Phase 4 — Semantic search across all recordings. Returns answer + source citations. |
| `/status` | Shows total recordings per person, last prompt sent, next prompt scheduled |
| `/history [name]` | Lists last 10 recordings for Mom or Dad with titles and dates |
| `/prompt [name]` | Manually triggers a prompt to Mom or Dad outside the regular schedule |
| `/add [name]` | Adds a new family member with their Telegram chat ID |

### Bot messages to parents

| Message | Guidance |
|---|---|
| Prompt | Warm, conversational tone. Just the question. No instructions — they already know to reply with a voice note. |
| Nudge | Sent once if no response after 48 hours. E.g. "No rush at all — just whenever you feel like it! 💙" |
| Acknowledgment | After receiving a voice note: simple and warm. E.g. "Got it, thank you ♥" — nothing technical. |
| Error | If something fails on the backend, parents see nothing. Error notification goes to archivist only. |

---

## 12. Credentials & API Keys

### Complete .env file

```bash
# Telegram
TELEGRAM_BOT_TOKEN=              # From @BotFather on Telegram
ARCHIVIST_CHAT_ID=               # Your Telegram chat ID — message @userinfobot
MOM_CHAT_ID=                     # Mom's Telegram chat ID — she messages @userinfobot
DAD_CHAT_ID=                     # Dad's Telegram chat ID — same process

# Anthropic
ANTHROPIC_API_KEY=               # console.anthropic.com → API Keys

# Supabase
SUPABASE_URL=                    # supabase.com dashboard → Settings → API → Project URL
SUPABASE_KEY=                    # supabase.com dashboard → Settings → API → anon/public key

# Google Drive
GOOGLE_DRIVE_FOLDER_ID=          # Open root archive folder in Drive, copy ID from URL
GOOGLE_SERVICE_ACCOUNT_JSON=     # Path to downloaded service account JSON key file

# Schedule config
MOM_PROMPT_TIME=10:00            # Time to send Mom's daily prompt (24hr format)
DAD_PROMPT_TIME=10:00            # Time to send Dad's daily prompt
PROMPT_CADENCE_DAYS=2            # Days between prompts
MOM_TIMEZONE=America/New_York    # Mom's local timezone
DAD_TIMEZONE=America/New_York    # Dad's local timezone

# Obsidian
OBSIDIAN_VAULT_NAME=Family Archive   # Name of the root vault folder in Google Drive
```

### How to get each credential

**TELEGRAM_BOT_TOKEN**
1. Open Telegram and message `@BotFather`
2. Send `/newbot`
3. Follow prompts to name your bot
4. Copy the token BotFather sends you

**ARCHIVIST_CHAT_ID / MOM_CHAT_ID / DAD_CHAT_ID**
1. The person messages `@userinfobot` on Telegram
2. It replies with their chat ID number
3. Copy that number into the env var

**ANTHROPIC_API_KEY**
1. Go to `console.anthropic.com`
2. Create account or log in
3. Go to API Keys → Create Key
4. Copy immediately — it won't be shown again

**SUPABASE_URL and SUPABASE_KEY**
1. Go to `supabase.com` and create a free account
2. Create a new project
3. Go to Settings → API
4. Copy Project URL → `SUPABASE_URL`
5. Copy anon/public key → `SUPABASE_KEY`
6. Run the SQL in section 10 to create the recordings table

**GOOGLE_DRIVE_FOLDER_ID and GOOGLE_SERVICE_ACCOUNT_JSON**
1. Go to `console.cloud.google.com` and create a new project called `family-voice-archive`
2. Enable the Google Drive API for the project (APIs & Services → Enable APIs)
3. Go to IAM & Admin → Service Accounts → Create Service Account
4. Name it `family-archive-bot`, click through the steps
5. Click the service account → Keys tab → Add Key → JSON
6. Download the JSON file — save it securely, set path in env var
7. In Google Drive, create a folder called `Family Archive`
8. Right-click the folder → Share → paste the service account email (found in the JSON as `client_email`) → give Editor access
9. Open the folder in Drive, copy the ID from the URL (the long string after `/folders/`)

---

## 13. Python Dependencies (requirements.txt)

```
python-telegram-bot==20.7
anthropic>=0.25.0
google-api-python-client>=2.0.0
google-auth>=2.0.0
google-auth-httplib2>=0.2.0
supabase>=2.0.0
APScheduler>=3.10.0
python-dotenv>=1.0.0
pydub>=0.25.1
tenacity>=8.2.0
pytz>=2024.1
```

---

## 14. Deployment — Render

### Setup

| Setting | Value |
|---|---|
| Service type | **Background Worker** — not a Web Service. Background workers do not spin down on Render free tier. |
| Build command | `pip install -r requirements.txt` |
| Start command | `python main.py` |
| Environment variables | Add all .env variables in Render dashboard under Environment → Environment Variables |
| Region | Oregon (US West) or closest to you |
| Auto-deploy | Enable from main branch on GitHub |

### Local development

- Run `python main.py` locally — polling mode means it just works, no tunnel or webhook setup needed
- Use a `.env` file locally; Render uses its own environment variable dashboard in production
- Obsidian vault can be pointed at local test folder during development

---

## 15. Error Handling

| Scenario | Behaviour |
|---|---|
| Telegram API failure | Retry with exponential backoff via `tenacity`. Log error. Do not crash. |
| Claude API failure | Retry up to 3 times. If still failing, save raw audio to Drive flagged for manual transcription. Notify archivist. |
| Google Drive upload failure | Retry 3 times. If still failing, save locally as fallback and notify archivist. |
| Supabase failure | Log error, continue without embedding. Mark note as unembedded in a local log. Run embedding sweep on next restart. |
| Parent sends text (not voice) | Bot replies warmly: "Voice notes work best! Try holding the microphone button 🎙" Do not process text as a recording. |
| Unknown sender | Bot ignores messages from chat IDs not in the allowed list. Does not reply. |
| All backend errors | Send brief notification to archivist Telegram chat. Parents never see error messages. |

All external API calls should use `tenacity` for retry logic with exponential backoff.

---

## 16. Build Order & Phases

### Phase 1 — Core bot (start here)
- Telegram bot setup with polling mode
- Voice note handler: receive and download audio from Telegram
- Claude transcription: audio base64 → raw transcript
- Claude structuring: raw transcript → metadata JSON (title, themes, summary, stage directions)
- Google Drive upload: audio file with clean filename
- Obsidian note formatter: correct frontmatter + audio embed + transcript
- Google Drive upload: markdown note to correct folder path
- Archivist notification on successful save
- Basic error handling and logging

### Phase 2 — Prompt scheduler
- APScheduler integration inside main.py
- Rotating prompt bank in config.py (100 prompts minimum)
- Per-parent schedule with configurable time and timezone
- Nudge logic: single follow-up message if no response in 48 hours
- `/status` and `/history` commands

### Phase 3 — Embeddings
- Supabase pgvector table creation and schema (see Section 10)
- Embedding generation inserted into the Phase 1 pipeline after note save
- Metadata stored alongside vector: title, person, date, themes, file paths
- Unembedded note sweep on startup to catch any failures from previous runs

### Phase 4 — RAG query
- `/ask` command handler
- Question embedding + vector similarity search against Supabase
- Claude answer generation with source citations
- Result formatted in Telegram message with recording titles listed

---

## 17. Future Ideas (Out of Scope for v1)

- Add grandparents or other family members as additional respondents
- Photo support: parents send a photo with a voice note caption — both saved together in one note
- Annual summary: on January 1st, bot sends archivist a digest of the year's recordings by theme
- Shareable private web view for siblings to browse the archive
- Birthday prompts: on the archivist's birthday, parents get special prompts about memories of that day
- Transcript corrections: archivist replies to a notification with a correction and the note gets updated automatically