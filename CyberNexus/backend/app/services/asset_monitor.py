
import platform
import socket
import uuid
import re
import subprocess
from datetime import datetime, timezone


def discover_local_asset():
    """Collect basic information about the authorized local device."""
    hostname = socket.gethostname()

    try:
        local_ip = socket.gethostbyname(hostname)
    except socket.gaierror:
        local_ip = None

    mac_address = ":".join(
        f"{(uuid.getnode() >> shift) & 0xff:02x}"
        for shift in range(40, -1, -8)
    )

    return {
        "hostname": hostname,
        "ip_address": local_ip,
        "mac_address": mac_address,
        "operating_system": platform.system(),
        "os_version": platform.release(),
        "status": "online",
        "discovered_at": datetime.now(timezone.utc).isoformat(),
    }


def discover_network_assets():
    """Discover IP and MAC candidates from the Windows ARP cache."""
    if platform.system() != "Windows":
        raise RuntimeError(
            "ARP cache discovery currently supports Windows only."
        )

    result = subprocess.run(
        ["arp", "-a"],
        capture_output=True,
        text=True,
        timeout=10,
        check=True,
    )

    local_asset = discover_local_asset()
    local_ip = local_asset["ip_address"]

    pattern = re.compile(
        r"^\s*(\d{1,3}(?:\.\d{1,3}){3})"
        r"\s+([0-9a-fA-F-]{17})\s+dynamic\s*$",
        re.IGNORECASE,
    )

    assets = []
    seen_ips = set()

    for line in result.stdout.splitlines():
        match = pattern.match(line)

        if not match:
            continue

        ip_address, mac_address = match.groups()

        octets = ip_address.split(".")
        if any(not 0 <= int(octet) <= 255 for octet in octets):
            continue

        # Exclude multicast, broadcast, and this laptop.
        if int(octets[0]) >= 224:
            continue

        if ip_address == local_ip or ip_address in seen_ips:
            continue

        seen_ips.add(ip_address)

        assets.append({
            "hostname": None,
            "ip_address": ip_address,
            "mac_address": mac_address.replace("-", ":").lower(),
            "operating_system": "Unknown",
            "status": "unverified",
            "discovery_source": "arp_cache",
            "discovered_at": datetime.now(timezone.utc).isoformat(),
        })

    return assets


if __name__ == "__main__":
    import json

    print("Local asset:")
    print(json.dumps(discover_local_asset(), indent=4))

    print("\nNetwork discovery candidates:")
    print(json.dumps(discover_network_assets(), indent=4))
