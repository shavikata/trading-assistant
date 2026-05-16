from app.backtesting.backtester import run_backtest
from app.config.logging_config import setup_logging
from app.storage.database import get_connection
from app.storage.repositories import get_active_tickers
from app.storage.schema import create_schema


def main() -> None:
    setup_logging()

    with get_connection() as connection:
        create_schema(connection)

        tickers = get_active_tickers(connection)

        if not tickers:
            print("No active tickers found. Run refresh_universe first.")
            return

        result = run_backtest(connection, tickers)

    print(f"Backtest finished: {result}")


if __name__ == "__main__":
    main()