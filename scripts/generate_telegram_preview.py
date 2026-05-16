from pathlib import Path

from app.config.logging_config import setup_logging
from app.storage.database import get_connection
from app.storage.schema import create_schema
from app.telegram_bot.message_formatter import build_latest_telegram_signal_message


def main() -> None:
    setup_logging()

    with get_connection() as connection:
        create_schema(connection)
        message = build_latest_telegram_signal_message(connection)

    output_path = Path("data/reports/latest_telegram_message.txt")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(message, encoding="utf-8")

    print(message)
    print(f"\nTelegram preview saved to: {output_path}")


if __name__ == "__main__":
    main()