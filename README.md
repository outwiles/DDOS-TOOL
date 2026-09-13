# DDOS-TOOL

<p align="center">
  <img src="assets/ddos.jpg" width="220" alt="Aashu logo" />
</p>


**Author / Developer / Admin / Owner:** Aashu
**GitHub:** [@outwiles](https://github.com/outwiles)
**Telegram:** [@outwiles](https://t.me/outwiles)
**Email:** [outwiles@proton.me](mailto:outwiles@proton.me)

A Python HTTP/2 stress-testing toolkit for authorized security testing. Modular, proxy-capable, and tuned for maximum request throughput against modern TLS/h2 targets.

## Features

- HTTP/2 with automatic ALPN negotiation, falls back to h1 where h2 isn't offered
- Cache-busted GET flood with rotating paths and randomized browser-realistic headers
- Session-per-proxy reuse with per-proxy concurrency caps
- Proxy pool: validation, startup probe against the real target, lazy eviction
- HTTPS targets accept only tunneling proxies (socks4/socks5/https)
- Live `Sent` / `Failed` per request, plus a summary line every 10s
- cfonts DDOS banner at startup
- Runs infinitely until Ctrl+C
- Cross-platform: Windows, Linux, macOS, Termux
- Interactive prompts, or skip with environment variables

## Architecture

```
DDOS-TOOL/
├── main.py                entrypoint, banner, prompts, orchestration
├── requirements.txt
├── README.md
├── LICENSE
├── proxies.txt
└── core/
    ├── __init__.py
    ├── config.py          constants
    ├── banner.py          cfonts banner
    ├── headers.py         UA pool, header randomization
    ├── proxies.py         proxy loading, validation, probing, rotation
    ├── client.py          httpx client factory
    ├── runner.py          worker loop, stats, emit
    └── vectors.py         paths, cache-busting, URL assembly
```

## Install

### Linux (Debian / Ubuntu / Kali)

```bash
sudo apt update && sudo apt install -y python3 python3-pip python3-venv git
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

### macOS

```bash
brew install python git
git clone https://github.com/outwiles/DDOS-TOOL.git
cd DDOS-TOOL
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

### Windows

```powershell
winget install Python.Python.3.12
git clone https://github.com/outwiles/DDOS-TOOL.git
cd DDOS-TOOL
python -m venv .venv
.\.venv\Scripts\Activate.ps1
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

## Run

```bash
python main.py
```

Prompts:

```
Target URL/IP: https://target.com
Do you want to use proxies? (y/n) [n]: y
Proxy file path [proxies.txt]: proxies.txt
```

Then runs at max concurrency until Ctrl+C.

Live output:

```
Sent
Sent
Failed
Sent
--- summary sent=4123 failed=211 proxies=48/51 ---
Sent
Failed
```

## Environment variables

```bash
export AASHU_TARGET="https://example.com"
export AASHU_PROXIES="proxies.txt"
python main.py
```

## Proxy format

`proxies.txt`, one per line:

```
socks5://user:pass@host:port
socks5://host:port
http://host:port
```

## Tuning

All constants live in `core/config.py` as `AASHU` through `AASHU12`.

## Legal

Only use this against systems you own or have explicit written authorization to test.

## Keywords

ddos tool, ddos attack script, ddos python, http flood, http/2 flood, slowloris, tcp syn flood, udp flood, stress testing tool, load testing tool, proxy rotation, proxy pool, origin concealment, ip masking, red team tool, penetration testing, offensive security, network stress test, authorized security testing, ddos github, aashu, outwiles

## License

MIT © Aashu
