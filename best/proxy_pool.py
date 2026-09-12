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
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import aiohttp
from aiohttp_socks import ProxyConnector


@dataclass
class ProxyEntry:
    url: str
    failures: int = 0
    success: int = 0
    latency_ms: float = 0.0
    alive: bool = True
    _lock: asyncio.Lock = field(default_factory=asyncio.Lock)

    @property
    def weight(self) -> float:
        if not self.alive:
            return 0.0
        base = max(1.0, 100.0 - self.latency_ms)
        return base / (1 + self.failures)

    async def mark_success(self, latency_ms: float):
        async with self._lock:
            self.success += 1
            if self.latency_ms:
                self.latency_ms = 0.7 * self.latency_ms + 0.3 * latency_ms
            else:
                self.latency_ms = latency_ms

    async def mark_failure(self, max_failures: int):
        async with self._lock:
            self.failures += 1
            if self.failures >= max_failures:
                self.alive = False


class ProxyPool:
    def __init__(
        self,
        proxy_file: str,
        health_check_url: str,
        max_failures: int = 3,
        rotate: str = "round_robin",
        health_check_concurrency: int = 100,
    ):
        self.proxy_file = Path(proxy_file)
        self.health_check_url = health_check_url
        self.max_failures = max_failures
        self.rotate = rotate
        self.hc_concurrency = health_check_concurrency
        self.proxies: list[ProxyEntry] = []
        self._rr_index = 0
        self._rr_lock = asyncio.Lock()

    def load(self) -> int:
        if not self.proxy_file.exists():
            raise FileNotFoundError(f"proxy file missing: {self.proxy_file}")
        lines = [ln.strip() for ln in self.proxy_file.read_text().splitlines()]
        lines = [ln for ln in lines if ln and not ln.startswith("#")]
        self.proxies = [ProxyEntry(url=ln) for ln in lines]
        return len(self.proxies)

    async def health_check(self):
        sem = asyncio.Semaphore(self.hc_concurrency)

        async def _check(entry: ProxyEntry):
            async with sem:
                connector = ProxyConnector.from_url(entry.url, rdns=True)
                start = asyncio.get_event_loop().time()
                try:
                    timeout = aiohttp.ClientTimeout(total=10)
                    async with aiohttp.ClientSession(connector=connector, timeout=timeout) as s:
                        async with s.get(self.health_check_url) as r:
                            if r.status == 200:
                                latency = (asyncio.get_event_loop().time() - start) * 1000
                                await entry.mark_success(latency)
                                return
                except Exception:
                    pass
                await entry.mark_failure(max_failures=1)

        await asyncio.gather(*(_check(e) for e in self.proxies))
        self.proxies = [p for p in self.proxies if p.alive]

    async def acquire(self) -> Optional[ProxyEntry]:
        alive = [p for p in self.proxies if p.alive]
        if not alive:
            return None

        if self.rotate == "random":
            return random.choice(alive)

        if self.rotate == "weighted":
            weights = [p.weight for p in alive]
            total = sum(weights)
            if total <= 0:
                return random.choice(alive)
            r = random.uniform(0, total)
            upto = 0.0
            for p, w in zip(alive, weights):
                upto += w
                if upto >= r:
                    return p
            return alive[-1]

        async with self._rr_lock:
            entry = alive[self._rr_index % len(alive)]
            self._rr_index += 1
            return entry

    async def report(self, entry: ProxyEntry, ok: bool, latency_ms: float = 0.0):
        if ok:
            await entry.mark_success(latency_ms)
        else:
            await entry.mark_failure(self.max_failures)

    def stats(self) -> dict:
        alive = sum(1 for p in self.proxies if p.alive)
        return {"total": len(self.proxies), "alive": alive, "dead": len(self.proxies) - alive}
