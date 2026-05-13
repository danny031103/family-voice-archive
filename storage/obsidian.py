"""Format markdown notes with frontmatter and inline audio embed for Obsidian."""
# Imports planned:
# import datetime
# from config import OBSIDIAN_VAULT_NAME

# Note format:
#   ---
#   title: <title>
#   date: YYYY-MM-DD
#   person: <person>
#   themes: [<theme1>, <theme2>]
#   prompt: <original prompt>
#   ---
#   # <title>
#
#   ![[YYYY-MM-DD-person-slug.ogg]]
#
#   ## Summary
#   <summary>
#
#   ## Transcript
#   <transcript with stage directions inline>


def format_note(
    title: str,
    date: str,
    person: str,
    themes: list,
    prompt: str,
    summary: str,
    transcript: str,
    audio_filename: str,
) -> str:
    """Return formatted markdown string ready for Obsidian."""
    # TODO: build YAML frontmatter block
    # TODO: add heading, audio embed (![[filename.ogg]])
    # TODO: add Summary section
    # TODO: add Transcript section
    # TODO: return complete markdown string
    pass


def make_slug(title: str) -> str:
    """Convert title to lowercase-hyphenated slug for filenames."""
    # TODO: lowercase, replace spaces/special chars with hyphens, strip leading/trailing
    pass


def make_audio_filename(date: str, person: str, title: str) -> str:
    """Return YYYY-MM-DD-person-slug.ogg filename."""
    # TODO: combine date + person + slug
    pass


def make_note_filename(date: str, title: str) -> str:
    """Return YYYY-MM-DD-slug.md filename."""
    # TODO: combine date + slug
    pass
