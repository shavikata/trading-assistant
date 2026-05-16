from __future__ import annotations

import pytest

from app.telegram_bot.sender import TelegramSendError, send_telegram_message


class FakeTelegramResponse:
    def __init__(self, status_code: int, payload: dict[str, object]) -> None:
        self.status_code = status_code
        self._payload = payload
        self.text = str(payload)

    def json(self) -> dict[str, object]:
        return self._payload


def test_send_telegram_message_posts_to_telegram(monkeypatch: pytest.MonkeyPatch) -> None:
    def fake_post(
        url: str,
        json: dict[str, object],
        timeout: int,
    ) -> FakeTelegramResponse:
        assert url == "https://api.telegram.org/botTOKEN/sendMessage"
        assert json["chat_id"] == "123"
        assert json["text"] == "hello"
        assert timeout == 15

        return FakeTelegramResponse(
            status_code=200,
            payload={"ok": True, "result": {"message_id": 99}},
        )

    monkeypatch.setattr("app.telegram_bot.sender.requests.post", fake_post)

    result = send_telegram_message(
        token="TOKEN",
        chat_id="123",
        message="hello",
    )

    assert result["ok"] is True
    assert result["result"] == {"message_id": 99}


def test_send_telegram_message_requires_token() -> None:
    with pytest.raises(TelegramSendError, match="TELEGRAM_BOT_TOKEN"):
        send_telegram_message(
            token="",
            chat_id="123",
            message="hello",
        )


def test_send_telegram_message_raises_on_api_error(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    def fake_post(
        url: str,
        json: dict[str, object],
        timeout: int,
    ) -> FakeTelegramResponse:
        return FakeTelegramResponse(
            status_code=200,
            payload={"ok": False, "description": "Bad Request"},
        )

    monkeypatch.setattr("app.telegram_bot.sender.requests.post", fake_post)

    with pytest.raises(TelegramSendError, match="Bad Request"):
        send_telegram_message(
            token="TOKEN",
            chat_id="123",
            message="hello",
        )