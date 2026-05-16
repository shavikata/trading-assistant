import logging

from app.signals.signal_engine import generate_signal_for_ticker
from app.storage.database import get_connection
from app.storage.repositories import get_active_tickers, insert_pipeline_run
from app.storage.schema import create_schema

logger = logging.getLogger(__name__)


def run_daily_signal_job() -> dict[str, int]:
    created_signals = 0

    with get_connection() as connection:
        create_schema(connection)

        tickers = get_active_tickers(connection)

        for ticker in tickers:
            price_rows = connection.execute(
                """
                SELECT ticker, date, open, high, low, close, adj_close, volume
                FROM price_data
                WHERE ticker = ?
                ORDER BY date ASC;
                """,
                (ticker,),
            ).fetchall()

            signal = generate_signal_for_ticker(ticker=ticker, price_rows=price_rows)

            if signal is None:
                print(f"{ticker}: no signal")
                continue

            connection.execute(
                """
                INSERT INTO signals (
                    ticker,
                    signal_date,
                    close_price,
                    volume,
                    avg_volume_20,
                    volume_spike_ratio,
                    atr_14,
                    atr_14_prev,
                    atr_compression_ratio,
                    rsi_14,
                    high_52w,
                    distance_from_52w_high_pct,
                    entry_price,
                    stop_loss,
                    target_1,
                    target_2,
                    score,
                    reason,
                    status
                )
                VALUES (
                    :ticker,
                    :signal_date,
                    :close_price,
                    :volume,
                    :avg_volume_20,
                    :volume_spike_ratio,
                    :atr_14,
                    :atr_14_prev,
                    :atr_compression_ratio,
                    :rsi_14,
                    :high_52w,
                    :distance_from_52w_high_pct,
                    :entry_price,
                    :stop_loss,
                    :target_1,
                    :target_2,
                    :score,
                    :reason,
                    :status
                )
                ON CONFLICT(ticker, signal_date) DO UPDATE SET
                    close_price = excluded.close_price,
                    volume = excluded.volume,
                    avg_volume_20 = excluded.avg_volume_20,
                    volume_spike_ratio = excluded.volume_spike_ratio,
                    atr_14 = excluded.atr_14,
                    atr_14_prev = excluded.atr_14_prev,
                    atr_compression_ratio = excluded.atr_compression_ratio,
                    rsi_14 = excluded.rsi_14,
                    high_52w = excluded.high_52w,
                    distance_from_52w_high_pct = excluded.distance_from_52w_high_pct,
                    entry_price = excluded.entry_price,
                    stop_loss = excluded.stop_loss,
                    target_1 = excluded.target_1,
                    target_2 = excluded.target_2,
                    score = excluded.score,
                    reason = excluded.reason,
                    status = excluded.status;
                """,
                signal.to_signal_table_row(),
            )

            created_signals += 1
            print(f"{ticker}: SIGNAL score={signal.score} | {signal.reason}")

        connection.commit()

        insert_pipeline_run(
            connection=connection,
            status="success",
            message="Daily signal scan completed.",
            universe_count=len(tickers),
            signals_count=created_signals,
        )

    return {
        "tickers_scanned": len(tickers),
        "signals_created": created_signals,
    }