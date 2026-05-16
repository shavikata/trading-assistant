from app.backtesting.backtester import create_backtest_schema
from app.config.logging_config import setup_logging
from app.reports.signal_report import build_latest_signal_reports
from app.reports.watchlist_report import build_watchlist_summary_report
from app.storage.database import get_connection
from app.storage.schema import create_schema


def main() -> None:
    setup_logging()

    with get_connection() as connection:
        create_schema(connection)
        create_backtest_schema(connection)

        reports = build_latest_signal_reports(
            connection=connection,
            limit=5,
        )

        if reports:
            for report in reports:
                print("\n" + "=" * 70)
                print(report.text)

            print("\n" + "=" * 70)
            return

        print("\n" + "=" * 70)
        print(build_watchlist_summary_report(connection))
        print("\n" + "=" * 70)


if __name__ == "__main__":
    main()