from __future__ import annotations

import argparse
import logging

from docucontrol.services.returns import GaiaReturnService, ProdocReturnService, TRReturnService

log = logging.getLogger(__name__)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Procesa devoluciones por email.")
    parser.add_argument("--vendor", choices=["tr", "gaia", "prodoc"], required=True, help="Cliente/bandeja a procesar.")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    service_map = {
        "tr": TRReturnService,
        "gaia": GaiaReturnService,
        "prodoc": ProdocReturnService,
    }
    service = service_map[args.vendor]()
    results = service.run()
    log.info("Procesados %s correos de %s", len(results), args.vendor.upper())


if __name__ == "__main__":
    main()

