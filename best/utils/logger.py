"""
DDOS-TOOL

Author / Developer / Admin / Owner: Aashu
GitHub:  @outwiles
Telegram: @outwiles
Email:   outwiles@proton.me

License: MIT
"""

import logging
import sys


def get_logger(cfg: dict) -> logging.Logger:
    logger = logging.getLogger("ddos")
    logger.setLevel(getattr(logging, cfg["logging"]["level"].upper(), logging.INFO))
    logger.handlers.clear()

    fmt = logging.Formatter("%(asctime)s %(levelname)s %(message)s")

    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(fmt)
    logger.addHandler(sh)

    if cfg["logging"].get("file"):
        fh = logging.FileHandler(cfg["logging"]["file"])
        fh.setFormatter(fmt)
        logger.addHandler(fh)

    return logger
