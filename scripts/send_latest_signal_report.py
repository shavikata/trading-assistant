from app.backtesting.backtester import create_backtest_schema
from app.config.logging_config import setup_logging
from app.reports.signal_report import build_latest_signal_reports
from app.reports.watchlist_report import build_watchlist_summary_report
from app.storage.database import get_connection
from app.storage.schema import create_schema
from app.telegram_bot.bot import send_telegram_message


def main() -> None:
    setup_logging()

    with get_connection() as connection:
        create_schema(connection)
        create_backtest_schema(connection)

        reports = build_latest_signal_reports(
            connection=connection,
            limit=1,
        )

        if reports:
            text = reports[0].text
            title = f"Latest signal sent: {reports[0].ticker} / {reports[0].signal_date}"
        else:
            text = build_watchlist_summary_report(connection)
            title = "No active signal. Watchlist summary sent."

    result = send_telegram_message(text)

    if result.ok:
        print(result.message)
        print(title)
        return

    print(result.message)


if __name__ == "__main__":
    main()