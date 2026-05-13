"""APScheduler cadence — prompts every N days per parent, nudge if no reply in 48h."""
import datetime
import logging

import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.date import DateTrigger

from config import (
    DAD_CHAT_ID,
    DAD_PROMPT_TIME,
    DAD_TIMEZONE,
    MOM_CHAT_ID,
    MOM_PROMPT_TIME,
    MOM_TIMEZONE,
    PROMPT_BANK,
    PROMPT_CADENCE_DAYS,
)
from bot.state import default_person_state, load_state, save_state

logger = logging.getLogger(__name__)

_NUDGE_HOURS = 48


def build_scheduler(app) -> AsyncIOScheduler:
    """Create and return a configured AsyncIOScheduler attached to the bot app."""
    scheduler = AsyncIOScheduler()

    for person_name, chat_id, prompt_time, timezone_str in [
        ("Mom", MOM_CHAT_ID, MOM_PROMPT_TIME, MOM_TIMEZONE),
        ("Dad", DAD_CHAT_ID, DAD_PROMPT_TIME, DAD_TIMEZONE),
    ]:
        if not chat_id:
            continue

        hour, minute = prompt_time.split(":")
        tz = pytz.timezone(timezone_str)

        scheduler.add_job(
            send_prompt,
            trigger=CronTrigger(
                day=f"*/{PROMPT_CADENCE_DAYS}",
                hour=int(hour),
                minute=int(minute),
                timezone=tz,
            ),
            args=[app, chat_id, person_name],
            id=f"prompt_{person_name.lower()}",
            replace_existing=True,
        )

    return scheduler


async def send_prompt(app, chat_id: int, person_name: str) -> None:
    """Pick the next prompt and send it to the given chat."""
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

    # Schedule a one-shot nudge check 48h from now
    nudge_time = datetime.datetime.utcnow() + datetime.timedelta(hours=_NUDGE_HOURS)
    try:
        scheduler = app.bot_data.get("scheduler")
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
            # Already responded after the last prompt — no nudge needed
            return

    person_state["nudge_sent"] = True
    state[person_name] = person_state
    save_state(state)

    await app.bot.send_message(
        chat_id,
        "Just a gentle reminder — whenever you have a moment, I'd love to hear a story from you \U0001f499",
    )
    logger.info("Sent nudge to %s", person_name)
