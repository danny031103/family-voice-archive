"""Upload audio .ogg and markdown .md to Google Drive."""
import io
import logging

from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaFileUpload, MediaIoBaseUpload
from tenacity import retry, stop_after_attempt, wait_exponential, before_sleep_log

from config import GOOGLE_DRIVE_FOLDER_ID, GOOGLE_CLIENT_ID, GOOGLE_CLIENT_SECRET, GOOGLE_REFRESH_TOKEN

logger = logging.getLogger(__name__)

TOKEN_URI = "https://oauth2.googleapis.com/token"


def get_drive_service():
    """Return an authenticated Drive client using OAuth refresh token."""
    creds = Credentials(
        token=None,
        refresh_token=GOOGLE_REFRESH_TOKEN,
        client_id=GOOGLE_CLIENT_ID,
        client_secret=GOOGLE_CLIENT_SECRET,
        token_uri=TOKEN_URI,
    )
    return build("drive", "v3", credentials=creds, cache_discovery=False)


def ensure_folder(service, parent_id: str, folder_name: str) -> str:
    """Get or create a folder under parent_id. Returns folder ID."""
    query = (
        f"name='{folder_name}' and '{parent_id}' in parents "
        f"and mimeType='application/vnd.google-apps.folder' and trashed=false"
    )
    results = service.files().list(q=query, fields="files(id, name)").execute()
    files = results.get("files", [])
    if files:
        return files[0]["id"]

    # Create the folder
    metadata = {
        "name": folder_name,
        "mimeType": "application/vnd.google-apps.folder",
        "parents": [parent_id],
    }
    folder = service.files().create(body=metadata, fields="id").execute()
    logger.info("Created Drive folder '%s' under parent %s", folder_name, parent_id)
    return folder["id"]


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), before_sleep=before_sleep_log(logger, logging.WARNING))
async def upload_audio(file_path: str, person: str, filename: str) -> str:
    """Upload .ogg file to _audio/<person_lower>/ folder. Returns Drive file ID."""
    service = get_drive_service()
    person_lower = person.lower()

    audio_root_id = ensure_folder(service, GOOGLE_DRIVE_FOLDER_ID, "_audio")
    person_folder_id = ensure_folder(service, audio_root_id, person_lower)

    media = MediaFileUpload(file_path, mimetype="audio/ogg", resumable=False)
    file_metadata = {
        "name": filename,
        "parents": [person_folder_id],
    }
    uploaded = (
        service.files()
        .create(body=file_metadata, media_body=media, fields="id")
        .execute()
    )
    file_id = uploaded["id"]
    logger.info("Uploaded audio %s → Drive id=%s", filename, file_id)
    return file_id


@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10), before_sleep=before_sleep_log(logger, logging.WARNING))
async def upload_note(content: str, person: str, theme_folder: str, filename: str) -> str:
    """Upload .md note to <person>/<theme_folder>/. Returns Drive file path string."""
    service = get_drive_service()

    person_folder_id = ensure_folder(service, GOOGLE_DRIVE_FOLDER_ID, person)
    theme_folder_id = ensure_folder(service, person_folder_id, theme_folder)

    content_bytes = content.encode("utf-8")
    media = MediaIoBaseUpload(
        io.BytesIO(content_bytes), mimetype="text/plain", resumable=False
    )
    file_metadata = {
        "name": filename,
        "parents": [theme_folder_id],
    }
    service.files().create(body=file_metadata, media_body=media, fields="id").execute()

    drive_path = f"{person}/{theme_folder}/{filename}"
    logger.info("Uploaded note → %s", drive_path)
    return drive_path
