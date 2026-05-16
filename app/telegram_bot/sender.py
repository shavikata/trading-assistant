from __future__ import annotations

import requests


class TelegramSendError(RuntimeError):
    pass


def send_telegram_message(
    *,
    token: str,
    chat_id: str,
    message: str,
    timeout: int = 15,
) -> dict[str, object]:
    if not token:
        raise TelegramSendError("TELEGRAM_BOT_TOKEN is missing.")

    if not chat_id:
        raise TelegramSendError("TELEGRAM_CHAT_ID is missing.")

    if not message.strip():
        raise TelegramSendError("Telegram message is empty.")

    response = requests.post(
        url=f"https://api.telegram.org/bot{token}/sendMessage",
        json={
            "chat_id": chat_id,
            "text": message,
            "disable_web_page_preview": True,
        },
        timeout=timeout,
    )

    if response.status_code >= 400:
        raise TelegramSendError(
            f"Telegram API HTTP error {response.status_code}: {response.text}"
        )

    payload = response.json()

    if not payload.get("ok"):
        description = payload.get("description", "Unknown Telegram API error.")
        raise TelegramSendError(str(description))

    return payload