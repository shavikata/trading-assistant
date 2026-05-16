from app.config.logging_config import setup_logging
from app.config.settings import settings
from app.storage.database import get_connection
from app.storage.schema import create_schema
from app.telegram_bot.message_formatter import build_latest_telegram_signal_message
from app.telegram_bot.sender import send_telegram_message


def main() -> None:
    setup_logging()

    with get_connection() as connection:
        create_schema(connection)
        message = build_latest_telegram_signal_message(connection)

    result = send_telegram_message(
        token=settings.telegram_bot_token,
        chat_id=settings.telegram_chat_id,
        message=message,
    )

    telegram_result = result.get("result", {})

    if isinstance(telegram_result, dict):
        message_id = telegram_result.get("message_id", "unknown")
    else:
        message_id = "unknown"

    print(f"Telegram message sent. message_id={message_id}")


if __name__ == "__main__":
    main()