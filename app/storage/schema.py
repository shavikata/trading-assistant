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

CREATE INDEX IF NOT EXISTS idx_price_data_ticker_date
ON price_data(ticker, date);

CREATE INDEX IF NOT EXISTS idx_signals_date
ON signals(signal_date);

CREATE INDEX IF NOT EXISTS idx_signals_ticker
ON signals(ticker);
"""


def create_schema(connection: sqlite3.Connection) -> None:
    connection.executescript(SCHEMA_SQL)
    connection.commit()