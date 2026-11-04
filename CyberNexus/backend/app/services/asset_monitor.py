
import platform
import socket
import uuid
import re
import subprocess
import ipaddress
from datetime import datetime, timezone


def discover_local_asset():
    """Collect information about the local device."""
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
    """Discover IP and MAC candidates from Windows ARP cache."""
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

    local_ip = discover_local_asset()["ip_address"]

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

        try:
            parsed_ip = ipaddress.ip_address(ip_address)
        except ValueError:
            continue

        if not parsed_ip.is_global and not parsed_ip.is_private:
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


def verify_device_reachability(ip_address):
    """Check whether a device responds to one ICMP ping."""
    try:
        parsed_ip = ipaddress.ip_address(ip_address)

        if parsed_ip.version != 4:
            return False

        result = subprocess.run(
            ["ping", "-n", "1", "-w", "1000", str(parsed_ip)],
            capture_output=True,
            text=True,
            timeout=3,
        )

        return result.returncode == 0

    except (ValueError, subprocess.TimeoutExpired, OSError):
        return False


def verify_network_assets():
    """Check reachability of discovered network candidates."""
    assets = discover_network_assets()

    for asset in assets:
        reachable = verify_device_reachability(asset["ip_address"])

        asset["reachability"] = (
            "reachable" if reachable else "unreachable"
        )

        asset["verified_at"] = datetime.now(
            timezone.utc
        ).isoformat()

    return assets


if __name__ == "__main__":
    import json

    print("Local asset:")
    print(json.dumps(discover_local_asset(), indent=4))

    print("\nVerified network reachability:")
    print(json.dumps(verify_network_assets(), indent=4))
