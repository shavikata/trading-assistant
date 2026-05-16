from __future__ import annotations

from dataclasses import dataclass

import requests

from app.config.settings import settings


TELEGRAM_API_BASE_URL = "https://api.telegram.org"


@dataclass(frozen=True)
class TelegramSendResult:
    ok: bool
    message: str


def send_telegram_message(text: str) -> TelegramSendResult:
    if not settings.telegram_bot_token:
        return TelegramSendResult(
            ok=False,
            message="TELEGRAM_BOT_TOKEN is missing in .env",
        )

    if not settings.telegram_chat_id:
        return TelegramSendResult(
            ok=False,
            message="TELEGRAM_CHAT_ID is missing in .env",
        )

    chunks = _split_message(text)

    for chunk in chunks:
        response = requests.post(
            f"{TELEGRAM_API_BASE_URL}/bot{settings.telegram_bot_token}/sendMessage",
            json={
                "chat_id": settings.telegram_chat_id,
                "text": chunk,
                "disable_web_page_preview": True,
            },
            timeout=20,
        )

        if not response.ok:
            return TelegramSendResult(
                ok=False,
                message=f"Telegram error {response.status_code}: {response.text}",
            )

    return TelegramSendResult(
        ok=True,
        message=f"Sent {len(chunks)} Telegram message chunk(s).",
    )


def _split_message(text: str, max_length: int = 4000) -> list[str]:
    if len(text) <= max_length:
        return [text]

    chunks: list[str] = []
    current_chunk: list[str] = []
    current_length = 0

    for line in text.splitlines():
        line_length = len(line) + 1

        if current_length + line_length > max_length:
            chunks.append("\n".join(current_chunk))
            current_chunk = [line]
            current_length = line_length
        else:
            current_chunk.append(line)
            current_length += line_length

    if current_chunk:
        chunks.append("\n".join(current_chunk))

    return chunks