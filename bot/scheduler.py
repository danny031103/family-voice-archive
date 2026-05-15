"""APScheduler cadence — randomised prompts per parent, nudge if no reply in 48h."""
import datetime
import logging
import random

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.date import DateTrigger

from config import (
    DAD_CHAT_ID,
    DAD_TIMEZONE,
    MOM_CHAT_ID,
    MOM_TIMEZONE,
    PROMPT_BANK,
    PROMPT_CADENCE_MAX_DAYS,
    PROMPT_CADENCE_MIN_DAYS,
    PROMPT_HOUR_MAX,
    PROMPT_HOUR_MIN,
)
from bot.state import default_person_state, load_state, save_state

logger = logging.getLogger(__name__)

_NUDGE_HOURS = 48

_PEOPLE = [
    ("Mom", MOM_CHAT_ID, MOM_TIMEZONE),
    ("Dad", DAD_CHAT_ID, DAD_TIMEZONE),
]


def _random_next_dt(timezone_str: str) -> datetime.datetime:
    """Return a random future datetime within the configured window."""
    tz = pytz.timezone(timezone_str)
    now = datetime.datetime.now(tz)
    days_ahead = random.randint(PROMPT_CADENCE_MIN_DAYS, PROMPT_CADENCE_MAX_DAYS)
    hour = random.randint(PROMPT_HOUR_MIN, PROMPT_HOUR_MAX)
    minute = random.randint(0, 59)
    target = (now + datetime.timedelta(days=days_ahead)).replace(
        hour=hour, minute=minute, second=0, microsecond=0
    )
    return target


def _schedule_next(scheduler: AsyncIOScheduler, app, chat_id: int, person_name: str, timezone_str: str) -> None:
    run_at = _random_next_dt(timezone_str)
    scheduler.add_job(
        send_prompt,
        trigger=DateTrigger(run_date=run_at),
        args=[app, chat_id, person_name, timezone_str],
        id=f"prompt_{person_name.lower()}",
        replace_existing=True,
    )
    logger.info("Next prompt for %s scheduled at %s", person_name, run_at.isoformat())


def build_scheduler(app) -> AsyncIOScheduler:
    """Create and return a configured AsyncIOScheduler attached to the bot app."""
    scheduler = AsyncIOScheduler()

    for person_name, chat_id, timezone_str in _PEOPLE:
        if not chat_id:
            continue
        _schedule_next(scheduler, app, chat_id, person_name, timezone_str)

    return scheduler


async def send_prompt(app, chat_id: int, person_name: str, timezone_str: str | None = None) -> None:
    """Pick the next prompt, send it, then schedule the next random firing."""
    if timezone_str is None:
        timezone_str = next((tz for name, _, tz in _PEOPLE if name == person_name), "America/New_York")

    state = load_state()
    person_state = state.get(person_name, default_person_state())

    if not PROMPT_BANK:
        logger.warning("PROMPT_BANK is empty — cannot send prompt to %s", person_name)
        return

    index = person_state.get("prompt_index", 0) % len(PROMPT_BANK)
    prompt_text = PROMPT_BANK[index]

    now_iso = datetime.datetime.utcnow().isoformat()
    person_state["last_prompt_sent"] = now_iso
    person_state["last_prompt_text"] = prompt_text
    person_state["prompt_index"] = (index + 1) % len(PROMPT_BANK)
    person_state["nudge_sent"] = False
    state[person_name] = person_state
    save_state(state)

    await app.bot.send_message(chat_id, prompt_text)
    logger.info("Sent prompt to %s: %s", person_name, prompt_text[:60])

    scheduler = app.bot_data.get("scheduler")

    # Schedule next random prompt
    if scheduler is not None:
        _schedule_next(scheduler, app, chat_id, person_name, timezone_str)

    # Schedule a one-shot nudge check 48h from now
    nudge_time = datetime.datetime.utcnow() + datetime.timedelta(hours=_NUDGE_HOURS)
    try:
        if scheduler is not None:
            scheduler.add_job(
                send_nudge,
                trigger=DateTrigger(run_date=nudge_time),
                args=[app, chat_id, person_name],
                id=f"nudge_{person_name.lower()}",
                replace_existing=True,
            )
    except Exception as exc:
        logger.warning("Could not schedule nudge for %s: %s", person_name, exc)


async def send_nudge(app, chat_id: int, person_name: str) -> None:
    """Send a gentle nudge if no voice note was received in the 48h since the last prompt."""
    state = load_state()
    person_state = state.get(person_name, default_person_state())

    if person_state.get("nudge_sent"):
        return

    last_prompt_sent = person_state.get("last_prompt_sent")
    last_response_time = person_state.get("last_response_time")

    if last_prompt_sent is None:
        return

    prompt_dt = datetime.datetime.fromisoformat(last_prompt_sent)

    if last_response_time is not None:
        response_dt = datetime.datetime.fromisoformat(last_response_time)
        if response_dt >= prompt_dt:
            return

    person_state["nudge_sent"] = True
    state[person_name] = person_state
    save_state(state)

    await app.bot.send_message(
        chat_id,
        "Just a gentle reminder — whenever you have a moment, I'd love to hear a story from you \U0001f499",
    )
    logger.info("Sent nudge to %s", person_name)
