import logging

from app.config.logging_config import setup_logging
from app.config.settings import settings
from app.storage.database import get_connection
from app.storage.schema import create_schema


logger = logging.getLogger("init_db")


def main() -> None:
    setup_logging()

    logger.info("Initializing database at: %s", settings.database_path)

    with get_connection() as connection:
        create_schema(connection)

    logger.info("Database initialized successfully.")


if __name__ == "__main__":
    main()
