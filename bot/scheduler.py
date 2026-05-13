"""APScheduler cadence — prompts every 2 days per parent, nudge if no reply in 48h."""
# Imports planned:
# from apscheduler.schedulers.asyncio import AsyncIOScheduler
# from apscheduler.triggers.cron import CronTrigger
# import pytz
# from config import MOM_CHAT_ID, DAD_CHAT_ID, MOM_PROMPT_TIME, DAD_PROMPT_TIME
# from config import MOM_TIMEZONE, DAD_TIMEZONE, PROMPT_CADENCE_DAYS
# from processing.claude import pick_prompt
# import state  # local state tracking last prompt/response per person


def build_scheduler(app):
    """Create and return a configured AsyncIOScheduler attached to the bot app."""
    # TODO: create AsyncIOScheduler
    # TODO: add job for Mom: send prompt on cadence, respecting timezone
    # TODO: add job for Dad: send prompt on cadence, respecting timezone
    # TODO: add nudge job: if no reply within 48h, send a reminder
    # TODO: return scheduler (caller starts it)
    pass


async def send_prompt(app, chat_id, person_name):
    """Pick a prompt and send it to the given chat."""
    # TODO: select next unused prompt from the 100-prompt bank
    # TODO: record prompt sent timestamp in state
    # TODO: send via Telegram bot
    pass


async def send_nudge(app, chat_id, person_name):
    """Send a gentle nudge if no voice note received in 48h."""
    # TODO: check state for last response time
    # TODO: if overdue, send nudge message
    pass
