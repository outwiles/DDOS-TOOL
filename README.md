<p align="center">
  <img src="assets/ddos.jpg" width="220" alt="Aashu logo" />
</p>

<h1 align="center">Aashu – HTTP/2 Stress Testing Tool</h1>

<p align="center">
  A high‑performance asynchronous HTTP/2 load generator – designed to test the resilience of web servers under extreme conditions.
</p>

Note: This tool is intended for authorised security testing and performance benchmarking only. Unauthorised use against third‑party systems is illegal and unethical. Use at your own risk.

---

Features

· HTTP/2 reset flood – rapidly opens and cancels streams to exhaust server resources.

· Priority‑frame bombing – sends excessive priority updates per stream, increasing CPU overhead.

· Settings toggling – continuously flips SETTINGS_ENABLE_PUSH to confuse the server state machine.

· Optional proxy rotation – uses HTTP CONNECT proxies (IP:PORT per line) to distribute traffic and hide the source.

· Fully asynchronous – built with asyncio and the h2 library, scaling to thousands of concurrent connections.

· Cross‑platform – runs on Termux (Android), Linux, Windows, and macOS.

---

Installation

Termux (Android)

```bash
pkg update && pkg upgrade -y
pkg install python git -y
git clone https://github.com/outwiles/DDOS-TOOL.git
cd DDOS-TOOL
pip install -r requirements.txt
```

Linux / macOS

```bash
# Debian/Ubuntu
sudo apt update && sudo apt install python3 python3-pip git -y

# macOS (with Homebrew)
brew install python git

git clone https://github.com/outwiles/DDOS-TOOL.git
cd DDOS-TOOL
pip3 install -r requirements.txt
```

Windows

· Install Python 3.7+ from python.org
· Open Command Prompt (Admin) and run:

```cmd
git clone https://github.com/outwiles/DDOS-TOOL.git
cd DDOS-TOOL
pip install -r requirements.txt
```

---

Usage

Run the script:

```bash
python ddos.py
```

You will be interactively prompted for:

Prompt Description
Target URL/IP Domain or IP address (e.g., https://example.com or 192.168.1.1)
Use proxies? Type y to enable proxy rotation, n to run without
Proxy file path (if y) Path to a text file with one IP:PORT per line
Threads Number of parallel workers (default 80)
Connections per thread Number of HTTP/2 connections each worker opens (default 40)
Duration Test duration in seconds (0 = run until Ctrl+C)

Example session

```
Target URL/IP:
  └──> https://target.com

Do you want to use proxies? (y/n): y
Proxy file path:
  └──> proxies.txt

Threads [80]: 100
Connections per thread [40]: 50
Duration in seconds (0 = infinite): 120
```

While running, the tool displays active worker counts every 2 seconds. Press Ctrl+C to stop gracefully.

---

Proxy File Format

Each line must contain a valid HTTP CONNECT proxy:

```
192.168.1.10:8080
203.0.113.5:3128
...
```

Note: Only anonymous proxies without authentication are supported.

---

Environment Variables (Optional)

To skip interactive prompts, preset these variables:

Variable Purpose
AASHU_TARGET Target URL/IP
AASHU_THREADS Number of threads
AASHU_CONNS Connections per thread
AASHU_DURATION Duration in seconds
AASHU_PROXIES Path to proxy file (if set, proxy prompt is skipped)

Example:

```bash
export AASHU_TARGET="https://example.com"
export AASHU_THREADS=150
export AASHU_CONNS=60
export AASHU_DURATION=0
export AASHU_PROXIES="proxies.txt"
python aashu.py
```

---


Important Disclaimer

· This tool generates heavy network traffic and can cause service disruption.
· You must have explicit written permission from the system owner before testing.
· The author assumes no liability for any misuse or damage caused by this software.
· Use it only on your own infrastructure or during authorised penetration tests.

---

# Credits

<p align="center">
  <b>Developed by Aashu</b><br/><br/>
  <a href="https://t.me/outwiles">
    <img src="https://img.shields.io/badge/Telegram-@outwiles-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram" />
  </a>
  <a href="https://github.com/outwiles">
    <img src="https://img.shields.io/badge/GitHub-@outwiles-181717?style=for-the-badge&logo=github&logoColor=white" alt="GitHub" />
  </a>
  <a href="mailto:outwiles@proton.me">
    <img src="https://img.shields.io/badge/Mail-outwiles%40proton.me-D14836?style=for-the-badge&logo=protonmail&logoColor=white" alt="Mail" />
  </a>
</p>
