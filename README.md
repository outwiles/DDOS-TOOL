# DDOS-TOOL

<p align="center">
  <img src="assets/ddos.jpg" width="220" alt="Aashu logo" />
</p>

**AASHU**

**Author / Developer / Admin / Owner:** Aashu
**GitHub:** [@outwiles](https://github.com/outwiles)
**Telegram:** [@outwiles](https://t.me/outwiles)
**Email:** [outwiles@proton.me](mailto:outwiles@proton.me)

A two-part study in offensive HTTP tooling: a modular baseline toolkit (`best/`) and a lean single-file variant (`worst/`) that squeezes roughly 10% more throughput out of the same proxy pool at the same load.

## Contents

- `best/` — modular multi-vector toolkit with proxy rotation, health-checked pool, and origin concealment
- `worst/` — single-file lean variant; same target types, same concealment, faster on L7
- `banner.py` — plain-text banner renderer
- `HowToRun.md` — step-by-step run guide, OS by OS

## Why two?

`best/` is the modular reference — clean separation, health-checked proxy pool at startup, four vectors, cross-platform L4 support. `worst/` is the lean single-file variant that beats it on L7 throughput by caching sessions and connectors per proxy, skipping the startup health-check pass, and shipping a live stats loop. Pick `best/` for flexibility, `worst/` for raw L7 output.

## Vectors

| Vector | Layer | Platforms | Notes |
|---|---|---|---|
| `http_flood` | L7 | Windows, Linux, macOS, Termux | Rotating proxies, randomized headers, cache-busting |
| `slowloris` | L7 | Windows, Linux, macOS, Termux | Half-open sockets, drip-feed headers |
| `tcp_syn` | L4 | Linux, macOS (root) | Raw sockets, spoofed source. Windows/Termux non-root blocked |
| `udp_flood` | L4 | Linux, macOS (root) | Raw sockets, spoofed source. Windows/Termux non-root blocked |

`best/` supports all four. `worst/` is L7 only (`http_flood`).

## Target types

`http`, `telegram`, `discord` — the type only affects header preparation. All three are plain HTTP targets.

## Proxy format

`best/proxies.txt` and `worst/proxies.txt`, one per line:

```
socks5://user:pass@host:port
http://user:pass@host:port
```

## File tree

```
DDOS-TOOL/
├── README.md
├── HowToRun.md
├── LICENSE
├── requirements.txt
├── banner.py
├── best/
│   ├── __init__.py
│   ├── main.py
│   ├── config.yaml
│   ├── proxies.txt
│   ├── proxy_pool.py
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── ua_pool.py
│   │   ├── headers.py
│   │   └── logger.py
│   └── vectors/
│       ├── __init__.py
│       ├── http_flood.py
│       ├── slowloris.py
│       ├── tcp_syn.py
│       └── udp_flood.py
└── worst/
    ├── README.md
    ├── ddos_worst.py
    ├── proxies.txt
    └── requirements.txt
```

## Install

### Common — Python 3.10+

```bash
python --version
```

Need **3.10+**. Uses `X | None` unions and modern `asyncio`.

### Windows 10 / 11

```powershell
winget install Python.Python.3.12
git clone https://github.com/outwiles/DDOS-TOOL.git
cd DDOS-TOOL
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

If PowerShell blocks activation:

```powershell
Set-ExecutionPolicy -Scope CurrentUser -ExecutionPolicy RemoteSigned
```

L7 vectors run fine. **Raw socket vectors do not work on Windows.**

### Linux (Debian / Ubuntu / Kali)

```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv git
git clone https://github.com/outwiles/DDOS-TOOL.git
cd DDOS-TOOL
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Linux (Fedora / RHEL)

```bash
sudo dnf install -y python3 python3-pip git
git clone https://github.com/outwiles/DDOS-TOOL.git
cd DDOS-TOOL
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Linux (Arch)

```bash
sudo pacman -S python python-pip git
git clone https://github.com/outwiles/DDOS-TOOL.git
cd DDOS-TOOL
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### macOS (Intel + Apple Silicon)

```bash
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
brew install python git
git clone https://github.com/outwiles/DDOS-TOOL.git
cd DDOS-TOOL
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Termux (Android)

```bash
pkg update && pkg upgrade -y
pkg install -y python git clang
git clone https://github.com/outwiles/DDOS-TOOL.git
cd DDOS-TOOL
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

No root = no L4. L7 only.

**For detailed per-OS run commands, config tuning, and troubleshooting, see [HowToRun.md](HowToRun.md).**

## Running

### `best/` — baseline toolkit

Config-driven. Set `best/config.yaml`, then:

```bash
python -m best.main --config best/config.yaml --target example_web
```

### `worst/` — interactive lean variant

Prompts on run, no config file:

```bash
cd worst
python ddos_worst.py
```

You'll be asked for target, proxy use, threads, connections per thread, and duration. Or skip the prompts with env vars:

```bash
export AASHU_TARGET="https://example.com"
export AASHU_THREADS=150
export AASHU_CONNS=60
export AASHU_DURATION=60
export AASHU_PROXIES="proxies.txt"
python ddos_worst.py
```

Live output every 5 seconds:

```
[03:22:41] sent=18234 failed=411 rps=3646 proxies=38/42
```

See [worst/README.md](worst/README.md) for the full rundown on why it's faster.

## Config quick reference

`best/config.yaml`:

```yaml
attack:
  vector: http_flood
  concurrency: 500
  duration_sec: 300
  timeout_sec: 8

proxy:
  file: proxies.txt
  rotate: round_robin
  health_check_url: https://api.ipify.org

obfuscation:
  cache_buster: true
  randomize_headers: true
  jitter_ms: [10, 250]
```

Tuning:

- Higher concurrency does not mean more damage. Past ~1000 workers you're usually bottlenecked by your proxy pool or your own uplink. Watch `proxy stats` in the logs.
- Health check runs first. Dead proxies are dropped at startup. Bump `health_check_concurrency` to 200–500 for big lists.
- Jitter matters. `[50, 400]` for stealth, `[0, 20]` for raw throughput.

## Platform notes

### Windows

- Use **PowerShell 7** or Windows Terminal. Legacy `cmd.exe` mishandles UTF-8 output.
- Windows Defender may quarantine `best/` due to raw-socket imports. Add the repo folder to Defender exclusions for your own tests.
- `http_flood` and `slowloris` run on `WindowsSelectorEventLoopPolicy` (set automatically in `main.py` and `worst/ddos_worst.py`).
- Firewall prompt on first run is normal — accept for private networks only.

### Linux

- For `tcp_syn` / `udp_flood`, run as root or grant capability once:
  ```bash
  sudo setcap cap_net_raw+ep $(readlink -f .venv/bin/python)
  ```
- Kali: system Python is externally managed. Use a venv, never `pip install` globally.

### macOS

- Apple Silicon (M1/M2/M3): all deps have arm64 wheels. No Rosetta.
- Gatekeeper may prompt on first `sudo` run of a venv Python binary — allow it in System Settings → Privacy & Security.

### Termux

- No root = L7 only.
- `aiohttp_socks` needs `clang` for `cryptography` (installed above).
- 500 concurrent sockets will torch the battery. Keep on charge.

## Banner

```bash
python banner.py
```

Prints the AASHU banner in plain text with a short author block.

## Legal

You are responsible for what you run and where you point it. Only use this against systems you own or have explicit written authorization to test.

## License

MIT © Aashu
