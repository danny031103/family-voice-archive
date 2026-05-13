"""Upload audio .ogg and markdown .md to Google Drive."""
# Imports planned:
# from googleapiclient.discovery import build
# from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
# from google.oauth2 import service_account
# from config import GOOGLE_DRIVE_FOLDER_ID, GOOGLE_SERVICE_ACCOUNT_JSON
# from tenacity import retry, stop_after_attempt, wait_exponential

# Drive layout:
# Family Archive/
#   Mom/Childhood/   ← auto-created from Claude themes
#   _audio/mom/      ← all .ogg files
#   _index/          ← auto-generated overview notes


def get_drive_service():
    """Return an authenticated Google Drive service client."""
    # TODO: load service account credentials from GOOGLE_SERVICE_ACCOUNT_JSON path
    # TODO: build and return Drive v3 service
    pass


async def upload_audio(file_path: str, person: str, filename: str) -> str:
    """Upload .ogg file to _audio/<person>/ folder. Returns Drive file ID."""
    # TODO: ensure _audio/<person>/ folder exists (create if not)
    # TODO: upload file with correct MIME type
    # TODO: return Drive file ID / path string
    pass


async def upload_note(content: str, person: str, theme_folder: str, filename: str) -> str:
    """Upload .md note to <person>/<theme_folder>/. Returns Drive file path."""
    # TODO: ensure <person>/<theme_folder>/ folder exists (create if not)
    # TODO: upload markdown content as text/plain
    # TODO: return Drive file path string
    pass


def ensure_folder(service, parent_id: str, folder_name: str) -> str:
    """Get or create a folder under parent_id. Returns folder ID."""
    # TODO: search for existing folder with name under parent
    # TODO: create if not found
    # TODO: return folder ID
    pass
