import sqlite3

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS stock_universe (
    ticker TEXT PRIMARY KEY,
    company_name TEXT,
    exchange TEXT,
    market_cap INTEGER,
    currency TEXT,
    is_active INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS price_data (
    ticker TEXT NOT NULL,
    date TEXT NOT NULL,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    adj_close REAL,
    volume INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (ticker, date),
    FOREIGN KEY (ticker) REFERENCES stock_universe(ticker)
);

CREATE TABLE IF NOT EXISTS signals (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    signal_date TEXT NOT NULL,
    close_price REAL NOT NULL,
    volume INTEGER,
    avg_volume_20 REAL,
    volume_spike_ratio REAL,
    atr_14 REAL,
    atr_14_prev REAL,
    atr_compression_ratio REAL,
    rsi_14 REAL,
    high_52w REAL,
    distance_from_52w_high_pct REAL,
    entry_price REAL,
    stop_loss REAL,
    target_1 REAL,
    target_2 REAL,
    score INTEGER DEFAULT 0,
    reason TEXT,
    status TEXT DEFAULT 'open',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(ticker, signal_date),
    FOREIGN KEY (ticker) REFERENCES stock_universe(ticker)
);

CREATE TABLE IF NOT EXISTS pipeline_runs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    started_at TEXT DEFAULT CURRENT_TIMESTAMP,
    finished_at TEXT,
    status TEXT NOT NULL,
    message TEXT,
    universe_count INTEGER DEFAULT 0,
    price_rows_count INTEGER DEFAULT 0,
    signals_count INTEGER DEFAULT 0
);
"""


def create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA_SQL)

    _ensure_column(
        connection=connection,
        table_name="signals",
        column_name="score",
        column_definition="INTEGER DEFAULT 0",
    )
    _ensure_column(
        connection=connection,
        table_name="signals",
        column_name="reason",
        column_definition="TEXT",
    )

    connection.commit()


def _ensure_column(
    connection: sqlite3.Connection,
    table_name: str,
    column_name: str,
    column_definition: str,
) -> None:
    existing_columns = {
        str(row[1])
        for row in connection.execute(f"PRAGMA table_info({table_name});").fetchall()
    }

    if column_name not in existing_columns:
        connection.execute(
            f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_definition};"
        )