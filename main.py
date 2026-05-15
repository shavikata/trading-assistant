from app.storage.database import get_connection
from app.storage.repositories import get_database_summary
from app.storage.schema import create_schema


def main() -> None:
    with get_connection() as connection:
        create_schema(connection)
        summary = get_database_summary(connection)

    print("\nTrading Assistant")
    print("=================")
    print("Database is ready.\n")
    print("Current database summary:")

    for table_name, total_rows in summary.items():
        print(f"- {table_name}: {total_rows}")


if __name__ == "__main__":
    main()