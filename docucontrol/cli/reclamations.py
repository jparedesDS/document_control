from __future__ import annotations

import argparse
import logging

from docucontrol.services.reporting import ReclamationsService

log = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Genera correos de reclamaciones a partir del monitoring report.")
    parser.add_argument("--date", help="Fecha de referencia (dd-mm-YYYY).")
    parser.add_argument("--send", action="store_true", help="Abre Outlook con los correos generados.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    service = ReclamationsService()
    mails = service.generate_emails(reference_date=args.date)
    log.info("Generadas %s reclamaciones", len(mails))
    if args.send and mails:
        service.send_via_outlook(mails)


if __name__ == "__main__":
    main()

