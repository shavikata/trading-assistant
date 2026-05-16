from collections.abc import Callable

from app.config.logging_config import setup_logging
from scripts.download_market_data import main as download_market_data
from scripts.refresh_universe import main as refresh_universe
from scripts.run_backtest import main as run_backtest
from scripts.run_daily_signals import main as run_daily_signals
from scripts.send_latest_signal_report import main as send_latest_signal_report


def run_step(step_name: str, step_function: Callable[[], None]) -> None:
    print("\n" + "=" * 70)
    print(f"START: {step_name}")
    print("=" * 70)

    try:
        step_function()
    except Exception as error:
        print("\n" + "=" * 70)
        print(f"FAILED: {step_name}")
        print(f"ERROR: {error}")
        print("=" * 70)
        raise

    print("\n" + "=" * 70)
    print(f"DONE: {step_name}")
    print("=" * 70)


def main() -> None:
    setup_logging()

    steps: list[tuple[str, Callable[[], None]]] = [
        ("Refresh universe", refresh_universe),
        ("Download market data", download_market_data),
        ("Run daily signal scan", run_daily_signals),
        ("Run backtest", run_backtest),
        ("Send Telegram report", send_latest_signal_report),
    ]

    for step_name, step_function in steps:
        run_step(step_name, step_function)

    print("\n" + "=" * 70)
    print("DAILY PIPELINE FINISHED SUCCESSFULLY")
    print("=" * 70)


if __name__ == "__main__":
    main()