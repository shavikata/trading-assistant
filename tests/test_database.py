import sqlite3

from app.storage.repositories import get_database_summary, insert_pipeline_run
from app.storage.schema import create_schema


def test_schema_creates_core_tables() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    create_schema(connection)

    rows = connection.execute(
        "SELECT name FROM sqlite_master WHERE type = 'table';"
    ).fetchall()

    table_names = {row["name"] for row in rows}

    assert "stock_universe" in table_names
    assert "price_data" in table_names
    assert "signals" in table_names
    assert "pipeline_runs" in table_names


def test_database_summary_returns_zero_for_empty_tables() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    create_schema(connection)

    summary = get_database_summary(connection)

    assert summary == {
        "stock_universe": 0,
        "price_data": 0,
        "signals": 0,
        "pipeline_runs": 0,
    }


def test_insert_pipeline_run_creates_row() -> None:
    connection = sqlite3.connect(":memory:")
    connection.row_factory = sqlite3.Row

    create_schema(connection)

    run_id = insert_pipeline_run(
        connection=connection,
        status="success",
        message="test run",
        universe_count=0,
        price_rows_count=0,
        signals_count=0,
    )

    assert run_id == 1

    summary = get_database_summary(connection)
    assert summary["pipeline_runs"] == 1
