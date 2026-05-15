import sqlite3
from typing import Iterable, Mapping


def count_rows(connection: sqlite3.Connection, table_name: str) -> int:
    allowed_tables = {
        "stock_universe",
        "price_data",
        "signals",
        "pipeline_runs",
    }

    if table_name not in allowed_tables:
        raise ValueError(f"Table not allowed: {table_name}")

    row = connection.execute(f"SELECT COUNT(*) AS total FROM {table_name}").fetchone()
    return int(row["total"])


def get_database_summary(connection: sqlite3.Connection) -> dict[str, int]:
    return {
        "stock_universe": count_rows(connection, "stock_universe"),
        "price_data": count_rows(connection, "price_data"),
        "signals": count_rows(connection, "signals"),
        "pipeline_runs": count_rows(connection, "pipeline_runs"),
    }


def upsert_universe_rows(
    connection: sqlite3.Connection,
    rows: Iterable[Mapping],
) -> int:
    rows = list(rows)

    if not rows:
        return 0

    sql = """
    INSERT INTO stock_universe (
        ticker,
        company_name,
        exchange,
        market_cap,
        currency,
        is_active,
        updated_at
    )
    VALUES (
        :ticker,
        :company_name,
        :exchange,
        :market_cap,
        :currency,
        :is_active,
        CURRENT_TIMESTAMP
    )
    ON CONFLICT(ticker) DO UPDATE SET
        company_name = excluded.company_name,
        exchange = excluded.exchange,
        market_cap = excluded.market_cap,
        currency = excluded.currency,
        is_active = excluded.is_active,
        updated_at = CURRENT_TIMESTAMP;
    """

    connection.executemany(sql, rows)
    connection.commit()

    return len(rows)


def insert_pipeline_run(
    connection: sqlite3.Connection,
    status: str,
    message: str = "",
    universe_count: int = 0,
    price_rows_count: int = 0,
    signals_count: int = 0,
) -> int:
    sql = """
    INSERT INTO pipeline_runs (
        status,
        message,
        universe_count,
        price_rows_count,
        signals_count
    )
    VALUES (?, ?, ?, ?, ?);
    """

    cursor = connection.execute(
        sql,
        (
            status,
            message,
            universe_count,
            price_rows_count,
            signals_count,
        ),
    )
    connection.commit()

    return int(cursor.lastrowid)