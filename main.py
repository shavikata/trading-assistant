import sqlite3
from datetime import datetime

import pandas as pd
import yfinance as yf


DB_NAME = "market_data.db"

TRADING_WATCHLIST = [
    "SPY",
    "QQQ",
    "GLD",
    "NVDA",
    "TSLA",
    "AAPL",
    "MSFT",
    "AMD",
    "META",
    "AMZN",
    "GOOGL",
    "NFLX",
    "PLTR",
]

INVESTMENT_WATCHLIST = [
    "USAR",
    "LAC",
]


def connect_db():
    return sqlite3.connect(DB_NAME)


def init_db():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS price_snapshots (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            ticker TEXT NOT NULL,
            price REAL,
            previous_close REAL,
            change_percent REAL,
            volume INTEGER,
            avg_volume_20d REAL,
            volume_ratio REAL,
            volatility_20d REAL,
            signal TEXT,
            similar_cases INTEGER,
            win_rate_5d REAL,
            avg_return_5d REAL,
            worst_return_5d REAL
        )
        """
    )

    cursor.execute(
        """
        CREATE TABLE IF NOT EXISTS investment_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            created_at TEXT NOT NULL,
            ticker TEXT NOT NULL,
            company_name TEXT,
            thesis TEXT,
            risks TEXT,
            status TEXT
        )
        """
    )

    conn.commit()
    conn.close()


def generate_signal(change_percent, volatility_20d, volume_ratio):
    if volatility_20d is None or volume_ratio is None:
        return "Neutral"

    if volatility_20d == 0:
        return "Neutral"

    strong_move = abs(change_percent) >= volatility_20d * 1.5
    volume_confirmed = volume_ratio >= 1.1

    if change_percent > 0 and strong_move and volume_confirmed:
        return "Bullish momentum watch"

    if change_percent < 0 and strong_move and volume_confirmed:
        return "Bearish momentum watch"

    return "Neutral"


def calculate_backtest(history, signal):
    if signal == "Neutral":
        return {
            "similar_cases": 0,
            "win_rate_5d": None,
            "avg_return_5d": None,
            "worst_return_5d": None,
        }

    df = history.copy()

    df["daily_return"] = df["Close"].pct_change() * 100
    df["volatility_20d"] = df["daily_return"].abs().rolling(20).mean().shift(1)
    df["avg_volume_20d"] = df["Volume"].rolling(20).mean().shift(1)
    df["volume_ratio"] = df["Volume"] / df["avg_volume_20d"]
    df["future_5d_return"] = ((df["Close"].shift(-5) / df["Close"]) - 1) * 100

    df = df.dropna()

    if signal == "Bullish momentum watch":
        cases = df[
            (df["daily_return"] >= df["volatility_20d"] * 1.5)
            & (df["volume_ratio"] >= 1.1)
        ]
        directional_returns = cases["future_5d_return"]

    elif signal == "Bearish momentum watch":
        cases = df[
            (df["daily_return"] <= -df["volatility_20d"] * 1.5)
            & (df["volume_ratio"] >= 1.1)
        ]
        directional_returns = -cases["future_5d_return"]

    else:
        cases = pd.DataFrame()
        directional_returns = pd.Series(dtype=float)

    similar_cases = len(cases)

    if similar_cases == 0:
        return {
            "similar_cases": 0,
            "win_rate_5d": None,
            "avg_return_5d": None,
            "worst_return_5d": None,
        }

    win_rate_5d = (directional_returns > 0).mean() * 100
    avg_return_5d = directional_returns.mean()
    worst_return_5d = directional_returns.min()

    return {
        "similar_cases": similar_cases,
        "win_rate_5d": round(win_rate_5d, 2),
        "avg_return_5d": round(avg_return_5d, 2),
        "worst_return_5d": round(worst_return_5d, 2),
    }


def fetch_market_snapshot(ticker):
    stock = yf.Ticker(ticker)
    history = stock.history(period="1y")

    if history.empty or len(history) < 30:
        return None

    latest = history.iloc[-1]
    previous = history.iloc[-2]

    price = float(latest["Close"])
    previous_close = float(previous["Close"])
    change_percent = ((price - previous_close) / previous_close) * 100

    volume = int(latest["Volume"])
    avg_volume_20d = history["Volume"].iloc[-21:-1].mean()

    if avg_volume_20d == 0:
        volume_ratio = None
    else:
        volume_ratio = volume / avg_volume_20d

    daily_returns = history["Close"].pct_change() * 100
    volatility_20d = daily_returns.abs().iloc[-21:-1].mean()

    signal = generate_signal(
        change_percent=change_percent,
        volatility_20d=volatility_20d,
        volume_ratio=volume_ratio,
    )

    backtest = calculate_backtest(history, signal)

    return {
        "ticker": ticker,
        "price": round(price, 2),
        "previous_close": round(previous_close, 2),
        "change_percent": round(change_percent, 2),
        "volume": volume,
        "avg_volume_20d": round(avg_volume_20d, 2),
        "volume_ratio": round(volume_ratio, 2) if volume_ratio is not None else None,
        "volatility_20d": round(volatility_20d, 2),
        "signal": signal,
        "similar_cases": backtest["similar_cases"],
        "win_rate_5d": backtest["win_rate_5d"],
        "avg_return_5d": backtest["avg_return_5d"],
        "worst_return_5d": backtest["worst_return_5d"],
    }


def save_snapshot(snapshot):
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO price_snapshots (
            created_at,
            ticker,
            price,
            previous_close,
            change_percent,
            volume,
            avg_volume_20d,
            volume_ratio,
            volatility_20d,
            signal,
            similar_cases,
            win_rate_5d,
            avg_return_5d,
            worst_return_5d
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(timespec="seconds"),
            snapshot["ticker"],
            snapshot["price"],
            snapshot["previous_close"],
            snapshot["change_percent"],
            snapshot["volume"],
            snapshot["avg_volume_20d"],
            snapshot["volume_ratio"],
            snapshot["volatility_20d"],
            snapshot["signal"],
            snapshot["similar_cases"],
            snapshot["win_rate_5d"],
            snapshot["avg_return_5d"],
            snapshot["worst_return_5d"],
        ),
    )

    conn.commit()
    conn.close()


def run_market_scan():
    tickers = TRADING_WATCHLIST + INVESTMENT_WATCHLIST

    print("\nMarket scan started...")
    print("-" * 80)

    for ticker in tickers:
        snapshot = fetch_market_snapshot(ticker)

        if snapshot is None:
            print(f"{ticker}: data not found")
            continue

        save_snapshot(snapshot)

        print(
            f"{snapshot['ticker']} | "
            f"Price: ${snapshot['price']} | "
            f"Change: {snapshot['change_percent']}% | "
            f"Volatility20D: {snapshot['volatility_20d']}% | "
            f"VolumeRatio: {snapshot['volume_ratio']} | "
            f"Signal: {snapshot['signal']}"
        )

        if snapshot["signal"] != "Neutral":
            print(
                f"  Backtest 5D: cases={snapshot['similar_cases']}, "
                f"win_rate={snapshot['win_rate_5d']}%, "
                f"avg_return={snapshot['avg_return_5d']}%, "
                f"worst_return={snapshot['worst_return_5d']}%"
            )

    print("-" * 80)
    print("Scan saved to SQLite database.")


def show_latest_snapshots():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT ps.ticker, ps.price, ps.change_percent, ps.volume_ratio,
               ps.volatility_20d, ps.signal, ps.similar_cases,
               ps.win_rate_5d, ps.avg_return_5d, ps.worst_return_5d,
               ps.created_at
        FROM price_snapshots ps
        JOIN (
            SELECT ticker, MAX(id) AS max_id
            FROM price_snapshots
            GROUP BY ticker
        ) latest
        ON ps.id = latest.max_id
        ORDER BY ps.ticker
        """
    )

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("\nNo data yet. Run market scan first.")
        return

    print("\nLatest saved snapshots")
    print("-" * 100)

    for row in rows:
        (
            ticker,
            price,
            change_percent,
            volume_ratio,
            volatility_20d,
            signal,
            similar_cases,
            win_rate_5d,
            avg_return_5d,
            worst_return_5d,
            created_at,
        ) = row

        print(
            f"{ticker} | ${price} | Change: {change_percent}% | "
            f"VolRatio: {volume_ratio} | Vol20D: {volatility_20d}% | "
            f"Signal: {signal} | Cases: {similar_cases} | "
            f"WinRate5D: {win_rate_5d}% | Avg5D: {avg_return_5d}% | "
            f"Worst5D: {worst_return_5d}% | {created_at}"
        )


def add_investment_note():
    print("\nAdd investment note")
    print("-" * 40)

    ticker = input("Ticker, example LAC or USAR: ").upper().strip()
    company_name = input("Company name: ").strip()
    thesis = input("Investment thesis: ").strip()
    risks = input("Main risks: ").strip()
    status = input("Status, example Watchlist / Small position / Avoid: ").strip()

    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        INSERT INTO investment_notes (
            created_at,
            ticker,
            company_name,
            thesis,
            risks,
            status
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            datetime.now().isoformat(timespec="seconds"),
            ticker,
            company_name,
            thesis,
            risks,
            status,
        ),
    )

    conn.commit()
    conn.close()

    print("Investment note saved.")


def show_investment_notes():
    conn = connect_db()
    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT ticker, company_name, thesis, risks, status, created_at
        FROM investment_notes
        ORDER BY id DESC
        """
    )

    rows = cursor.fetchall()
    conn.close()

    if not rows:
        print("\nNo investment notes yet.")
        return

    print("\nInvestment notes")
    print("-" * 80)

    for row in rows:
        ticker, company_name, thesis, risks, status, created_at = row

        print(f"\nTicker: {ticker}")
        print(f"Company: {company_name}")
        print(f"Status: {status}")
        print(f"Thesis: {thesis}")
        print(f"Risks: {risks}")
        print(f"Created: {created_at}")


def main_menu():
    init_db()

    while True:
        print("\nTrading Assistant v0.2")
        print("=" * 40)
        print("1. Run market scan and save to database")
        print("2. Show latest market snapshots")
        print("3. Add investment note")
        print("4. Show investment notes")
        print("5. Exit")

        choice = input("\nChoose option: ").strip()

        if choice == "1":
            run_market_scan()
        elif choice == "2":
            show_latest_snapshots()
        elif choice == "3":
            add_investment_note()
        elif choice == "4":
            show_investment_notes()
        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("Invalid choice.")


if __name__ == "__main__":
    main_menu()