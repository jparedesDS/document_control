from __future__ import annotations

import argparse
import logging

from docucontrol.services.reporting import OVRReportService

log = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera reportes OVR.")
    parser.add_argument("--mode", choices=["simple", "union"], default="union", help="Tipo de reporte a generar.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    service = OVRReportService()
    if args.mode == "simple":
        result = service.generate_simple_report()
    else:
        result = service.generate_union_report()
    log.info("Reporte OVR generado en %s", result.output_path)


if __name__ == "__main__":
    main()

