from pathlib import Path

from app.config.logging_config import setup_logging
from app.reports.report_builder import build_latest_signal_report, save_report_to_file
from app.storage.database import get_connection
from app.storage.schema import create_schema


def main() -> None:
    setup_logging()

    with get_connection() as connection:
        create_schema(connection)

        report = build_latest_signal_report(connection)
        output_path = save_report_to_file(
            report=report,
            output_path=Path("data/reports/latest_signal_report.md"),
        )

    print(report)
    print(f"\nReport saved to: {output_path}")


if __name__ == "__main__":
    main()