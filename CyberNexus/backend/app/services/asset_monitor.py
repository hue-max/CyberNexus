import platform
import socket
import uuid
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


if __name__ == "__main__":
    import json
    print(json.dumps(discover_local_asset(), indent=4))