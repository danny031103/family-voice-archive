"""Entry point — starts Telegram polling + APScheduler."""
import logging
from dotenv import load_dotenv


def main():
    load_dotenv()
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s"
    )
    logging.info("Family Voice Archive started")


if __name__ == "__main__":
    main()
