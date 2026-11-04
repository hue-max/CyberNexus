
from app.services.database import get_connection


def register_asset(asset: dict) -> dict:
    """Save or update a verified, monitored asset."""
    connection = get_connection()

    try:
        cursor = connection.cursor()

        hostname = asset.get("hostname")
        ip_address = asset.get("ip_address")
        mac_address = asset.get("mac_address")
        operating_system = asset.get("operating_system") or "Unknown"

        if not hostname:
            raise ValueError("A hostname is required.")

        cursor.execute(
            """
            SELECT AssetID
            FROM dbo.Assets
            WHERE AssetName = ? OR IPAddress = ?
            """,
            (hostname, ip_address),
        )
        existing = cursor.fetchone()

        if existing:
            asset_id = existing[0]

            cursor.execute(
                """
                UPDATE dbo.Assets
                SET AssetName = ?,
                    IPAddress = ?,
                    MACAddress = COALESCE(?, MACAddress),
                    OperatingSystem = ?,
                    Status = 'Active',
                    ConsecutiveFailures = 0,
                    LastSeen = SYSUTCDATETIME()
                WHERE AssetID = ?
                """,
                (
                    hostname,
                    ip_address,
                    mac_address,
                    operating_system,
                    asset_id,
                ),
            )
        else:
            cursor.execute(
                """
                INSERT INTO dbo.Assets
                    (AssetName, AssetType, IPAddress, MACAddress,
                     OperatingSystem, Status, LastSeen,
                     ConsecutiveFailures)
                OUTPUT INSERTED.AssetID
                VALUES (?, 'Computer', ?, ?, ?, 'Active',
                        SYSUTCDATETIME(), 0)
                """,
                (hostname, ip_address, mac_address, operating_system),
            )
            asset_id = cursor.fetchone()[0]

        connection.commit()

        return {
            **asset,
            "asset_id": asset_id,
            "status": "online",
        }

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def register_discovered_asset(asset: dict) -> dict:
    """Store an ARP discovery candidate as unverified."""
    ip_address = asset.get("ip_address")
    mac_address = asset.get("mac_address")

    if not ip_address:
        raise ValueError("An IP address is required.")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT AssetID
            FROM dbo.Assets
            WHERE IPAddress = ?
            """,
            (ip_address,),
        )
        existing = cursor.fetchone()

        asset_name = asset.get("hostname") or f"Unknown-{ip_address}"
        operating_system = asset.get("operating_system") or "Unknown"

        if existing:
            asset_id = existing[0]

            cursor.execute(
                """
                UPDATE dbo.Assets
                SET MACAddress = COALESCE(?, MACAddress)
                WHERE AssetID = ?
                """,
                (mac_address, asset_id),
            )
        else:
            cursor.execute(
                """
                INSERT INTO dbo.Assets
                    (AssetName, AssetType, IPAddress, MACAddress,
                     OperatingSystem, Status, LastSeen,
                     ConsecutiveFailures)
                OUTPUT INSERTED.AssetID
                VALUES (?, 'Computer', ?, ?, ?, 'Unverified',
                        NULL, 0)
                """,
                (
                    asset_name,
                    ip_address,
                    mac_address,
                    operating_system,
                ),
            )
            asset_id = cursor.fetchone()[0]

        connection.commit()

        return {
            **asset,
            "asset_id": asset_id,
            "status": "unverified",
        }

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def list_assets() -> list:
    """Retrieve registered assets from SQL Server."""
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT AssetID, AssetName, AssetType, IPAddress,
                   MACAddress, OperatingSystem, Criticality,
                   Status, LastSeen, CreatedAt,
                   ConsecutiveFailures
            FROM dbo.Assets
            ORDER BY AssetID
            """
        )

        columns = [column[0] for column in cursor.description]

        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    finally:
        connection.close()


def mark_offline_assets(timeout_seconds: int = 120) -> int:
    """Mark stale active assets inactive only after two failures."""
    if timeout_seconds < 1:
        raise ValueError("timeout_seconds must be at least 1")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            UPDATE dbo.Assets
            SET Status = 'Inactive'
            WHERE Status = 'Active'
              AND ConsecutiveFailures >= 2
              AND (
                    LastSeen IS NULL
                    OR LastSeen < DATEADD(
                        SECOND, -?, SYSUTCDATETIME()
                    )
              )
            """,
            (timeout_seconds,),
        )

        affected = cursor.rowcount
        connection.commit()

        return affected

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def update_device_verification(asset: dict) -> dict:
    """Update asset status using consecutive ping failures."""
    connection = get_connection()

    try:
        cursor = connection.cursor()

        ip_address = asset.get("ip_address")
        mac_address = asset.get("mac_address")
        reachability = asset.get("reachability")

        if not ip_address:
            raise ValueError("IP address is required.")

        if reachability not in ("reachable", "unreachable"):
            raise ValueError("Invalid reachability result.")

        cursor.execute(
            """
            UPDATE dbo.Assets
            SET MACAddress = COALESCE(?, MACAddress),

                ConsecutiveFailures = CASE
                    WHEN ? = 'reachable' THEN 0
                    WHEN Status = 'Unverified' THEN 0
                    ELSE ConsecutiveFailures + 1
                END,

                Status = CASE
                    WHEN ? = 'reachable' THEN 'Active'
                    WHEN Status = 'Unverified' THEN 'Unverified'
                    WHEN ConsecutiveFailures + 1 >= 2
                        THEN 'Inactive'
                    ELSE Status
                END,

                LastSeen = CASE
                    WHEN ? = 'reachable'
                    THEN SYSUTCDATETIME()
                    ELSE LastSeen
                END

            WHERE IPAddress = ?
            """,
            (
                mac_address,
                reachability,
                reachability,
                reachability,
                ip_address,
            ),
        )

        cursor.execute(
            """
            SELECT Status, ConsecutiveFailures
            FROM dbo.Assets
            WHERE IPAddress = ?
            """,
            (ip_address,),
        )

        row = cursor.fetchone()

        actual_status = row[0] if row else "Not Found"
        failure_count = row[1] if row else None

        connection.commit()

        return {
            "ip_address": ip_address,
            "mac_address": mac_address,
            "reachability": reachability,
            "status": actual_status,
            "consecutive_failures": failure_count,
            "database_record_found": row is not None,
        }

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def save_monitoring_history(
    ip_address: str,
    reachability: str,
) -> dict:
    """Save a device reachability check in monitoring history."""
    if not ip_address:
        raise ValueError("IP address is required.")

    if reachability not in ("reachable", "unreachable"):
        raise ValueError("Invalid reachability result.")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO dbo.AssetMonitoringHistory
                (AssetID, Reachability)
            SELECT AssetID, ?
            FROM dbo.Assets
            WHERE IPAddress = ?
            """,
            (reachability, ip_address),
        )

        affected = cursor.rowcount
        connection.commit()

        return {
            "ip_address": ip_address,
            "reachability": reachability,
            "history_saved": affected > 0,
        }

    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def get_monitoring_history(limit: int = 100) -> list:
    """Retrieve recent device monitoring history."""
    if limit < 1:
        raise ValueError("Limit must be at least 1.")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            SELECT TOP (?)
                h.MonitoringID,
                h.AssetID,
                a.AssetName,
                a.IPAddress,
                a.MACAddress,
                h.Reachability,
                h.CheckedAt
            FROM dbo.AssetMonitoringHistory AS h
            INNER JOIN dbo.Assets AS a
                ON h.AssetID = a.AssetID
            ORDER BY h.CheckedAt DESC
            """,
            (limit,),
        )

        columns = [column[0] for column in cursor.description]

        return [
            dict(zip(columns, row))
            for row in cursor.fetchall()
        ]

    finally:
        connection.close()
