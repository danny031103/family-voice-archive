"""All env vars, constants, and the 100-prompt bank (populated in Phase 2)."""
import os
from dotenv import load_dotenv

load_dotenv()

# --- Telegram ---
TELEGRAM_BOT_TOKEN: str = os.environ["TELEGRAM_BOT_TOKEN"]
ARCHIVIST_CHAT_ID: int = int(os.environ["ARCHIVIST_CHAT_ID"])
MOM_CHAT_ID: int = int(os.environ["MOM_CHAT_ID"]) if os.environ.get("MOM_CHAT_ID") else 0
DAD_CHAT_ID: int = int(os.environ["DAD_CHAT_ID"]) if os.environ.get("DAD_CHAT_ID") else 0

# --- Anthropic ---
ANTHROPIC_API_KEY: str = os.environ["ANTHROPIC_API_KEY"]
CLAUDE_MODEL: str = "claude-sonnet-4-20250514"

# --- Supabase ---
SUPABASE_URL: str = os.environ["SUPABASE_URL"]
SUPABASE_KEY: str = os.environ["SUPABASE_KEY"]

# --- Google Drive ---
GOOGLE_DRIVE_FOLDER_ID: str = os.environ["GOOGLE_DRIVE_FOLDER_ID"]
GOOGLE_SERVICE_ACCOUNT_JSON: str = os.environ["GOOGLE_SERVICE_ACCOUNT_JSON"]

# --- Schedule config ---
MOM_PROMPT_TIME: str = os.environ.get("MOM_PROMPT_TIME", "10:00")
DAD_PROMPT_TIME: str = os.environ.get("DAD_PROMPT_TIME", "10:00")
PROMPT_CADENCE_DAYS: int = int(os.environ.get("PROMPT_CADENCE_DAYS", "2"))
MOM_TIMEZONE: str = os.environ.get("MOM_TIMEZONE", "America/New_York")
DAD_TIMEZONE: str = os.environ.get("DAD_TIMEZONE", "America/New_York")

# --- Obsidian ---
OBSIDIAN_VAULT_NAME: str = os.environ.get("OBSIDIAN_VAULT_NAME", "Family Archive")

# --- Feature flags ---
DRY_RUN: bool = os.environ.get("DRY_RUN", "false").lower() in ("true", "1", "yes")

# --- Allowed senders ---
ALLOWED_CHAT_IDS: dict[str, int] = {
    "Mom": MOM_CHAT_ID,
    "Dad": DAD_CHAT_ID,
}

# --- Prompt bank (populated in Phase 2) ---
PROMPT_BANK: list[str] = []
