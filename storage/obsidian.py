"""Format markdown notes with frontmatter and inline audio embed for Obsidian."""
import re


def make_slug(title: str) -> str:
    """Convert title to lowercase-hyphenated slug for filenames."""
    slug = title.lower()
    slug = re.sub(r"[^a-z0-9]+", "-", slug)
    slug = slug.strip("-")
    return slug


def make_audio_filename(date: str, person: str, title: str) -> str:
    """Return YYYY-MM-DD-person-slug.ogg filename."""
    slug = make_slug(title)
    return f"{date}-{person.lower()}-{slug}.ogg"


def make_note_filename(date: str, title: str) -> str:
    """Return YYYY-MM-DD-slug.md filename."""
    slug = make_slug(title)
    return f"{date}-{slug}.md"


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
    themes_inline = ", ".join(themes)
    person_lower = person.lower()

    note = f"""---
title: {title}
person: {person}
date: {date}
prompt: "{prompt}"
theme: [{themes_inline}]
summary: {summary}
audio: _audio/{person_lower}/{audio_filename}
---

## Prompt
"{prompt}"

## Voice Recording
![[{audio_filename}]]

## Transcript
{transcript}
"""
    return note
