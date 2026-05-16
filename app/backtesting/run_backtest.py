from app.backtesting.backtester import run_backtest
from app.config.logging_config import setup_logging
from app.storage.database import get_connection
from app.storage.repositories import get_active_tickers, insert_pipeline_run
from app.storage.schema import create_schema


def main() -> None:
    setup_logging()

    with get_connection() as connection:
        create_schema(connection)

        tickers = get_active_tickers(connection)

        result = run_backtest(connection, tickers)

        insert_pipeline_run(
            connection=connection,
            status="success",
            message="Backtest completed.",
            universe_count=len(tickers),
            signals_count=0,
        )

    print(f"Backtest finished: {result}")


if __name__ == "__main__":
    main()