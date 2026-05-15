import logging

from app.config.logging_config import setup_logging
from app.data.market_data import download_ohlcv
from app.storage.database import get_connection
from app.storage.repositories import (
    get_active_tickers,
    insert_pipeline_run,
    upsert_price_rows,
)
from app.storage.schema import create_schema

logger = logging.getLogger("download_market_data")


def main() -> None:
    setup_logging()

    total_price_rows = 0

    with get_connection() as connection:
        create_schema(connection)

        tickers = get_active_tickers(connection)

        if not tickers:
            message = "No active tickers found. Run scripts/refresh_universe.py first."
            logger.warning(message)
            print(message)
            return

        for ticker in tickers:
            try:
                rows = download_ohlcv(ticker=ticker, period="1y", interval="1d")
                inserted_count = upsert_price_rows(connection, rows)
                total_price_rows += inserted_count

                print(f"{ticker}: stored {inserted_count} rows")

            except Exception as error:
                logger.exception("Failed to download market data for %s", ticker)
                print(f"{ticker}: failed - {error}")

        insert_pipeline_run(
            connection=connection,
            status="success",
            message="Market data download completed.",
            universe_count=len(tickers),
            price_rows_count=total_price_rows,
        )

    print(f"Done. Stored {total_price_rows} price rows.")


if __name__ == "__main__":
    main()