import logging

from app.config.logging_config import setup_logging
from app.data.universe import get_mvp_watchlist
from app.storage.database import get_connection
from app.storage.repositories import insert_pipeline_run, upsert_universe_rows
from app.storage.schema import create_schema

logger = logging.getLogger("refresh_universe")


def main() -> None:
    setup_logging()

    rows = get_mvp_watchlist()

    with get_connection() as connection:
        create_schema(connection)

        universe_count = upsert_universe_rows(connection, rows)

        insert_pipeline_run(
            connection=connection,
            status="success",
            message="Static MVP watchlist refreshed.",
            universe_count=universe_count,
        )

    logger.info("Universe refreshed: %s tickers", universe_count)
    print(f"Universe refreshed: {universe_count} tickers")


if __name__ == "__main__":
    main()