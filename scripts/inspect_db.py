from app.config.logging_config import setup_logging
from app.storage.database import get_connection
from app.storage.repositories import get_database_summary


def main() -> None:
    setup_logging()

    with get_connection() as connection:
        summary = get_database_summary(connection)

    print("\nDatabase Summary")
    print("----------------")

    for table_name, total_rows in summary.items():
        print(f"{table_name}: {total_rows}")


if __name__ == "__main__":
    main()