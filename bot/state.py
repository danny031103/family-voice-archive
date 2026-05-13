"""State manager — reads/writes scheduler_state.json and recording_index.json."""
import json
import os

_STATE_DIR = os.path.join(os.path.dirname(__file__), "..", "state")
_STATE_FILE = os.path.join(_STATE_DIR, "scheduler_state.json")
_INDEX_FILE = os.path.join(_STATE_DIR, "recording_index.json")


def _ensure_state_dir() -> None:
    os.makedirs(_STATE_DIR, exist_ok=True)


def default_person_state() -> dict:
    return {
        "last_prompt_sent": None,
        "last_prompt_text": None,
        "last_response_time": None,
        "prompt_index": 0,
        "nudge_sent": False,
        "recording_count": 0,
    }


def load_state() -> dict:
    """Read scheduler_state.json; return default structure if missing."""
    if not os.path.exists(_STATE_FILE):
        return {}
    with open(_STATE_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_state(data: dict) -> None:
    """Write data to scheduler_state.json."""
    _ensure_state_dir()
    with open(_STATE_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def load_recording_index() -> list:
    """Read recording_index.json; return [] if missing."""
    if not os.path.exists(_INDEX_FILE):
        return []
    with open(_INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def append_recording(entry: dict) -> None:
    """Append an entry to recording_index.json."""
    _ensure_state_dir()
    index = load_recording_index()
    index.append(entry)
    with open(_INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(index, f, indent=2)
