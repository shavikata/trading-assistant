from app.config.logging_config import setup_logging
from app.jobs.daily_signal_job import run_daily_signal_job


def main() -> None:
    setup_logging()
    result = run_daily_signal_job()
    print(f"Daily signal job finished: {result}")


if __name__ == "__main__":
    main()