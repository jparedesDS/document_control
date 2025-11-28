from __future__ import annotations

import argparse
from datetime import datetime
import logging

from docucontrol.services.reporting import MonitoringReportService

log = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera el Monitoring Report sin GUI.")
    parser.add_argument("--date", help="Fecha de referencia (dd-mm-YYYY).")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    reference_date = datetime.strptime(args.date, "%d-%m-%Y") if args.date else None
    service = MonitoringReportService()
    result = service.run(reference_date=reference_date)
    log.info("Reporte generado en %s", result.output_path)


if __name__ == "__main__":
    main()

