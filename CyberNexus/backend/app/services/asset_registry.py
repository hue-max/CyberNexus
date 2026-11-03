
from app.services.database import get_connection


def register_asset(asset: dict) -> dict:
    """Save or update a verified, monitored asset."""
    connection = get_connection()

    try:
        cursor = connection.cursor()

        hostname = asset.get("hostname")
        ip_address = asset.get("ip_address")
        operating_system = asset.get("operating_system") or "Unknown"

        if not hostname:
            raise ValueError(
                "A hostname is required for verified asset registration."
            )

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
                    OperatingSystem = ?,
                    Status = 'Active',
                    LastSeen = SYSUTCDATETIME()
                WHERE AssetID = ?
                """,
                (hostname, ip_address, operating_system, asset_id),
            )
        else:
            cursor.execute(
                """
                INSERT INTO dbo.Assets
                    (AssetName, AssetType, IPAddress,
                     OperatingSystem, Status, LastSeen)
                OUTPUT INSERTED.AssetID
                VALUES (?, 'Computer', ?, ?, 'Active',
                        SYSUTCDATETIME())
                """,
                (hostname, ip_address, operating_system),
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

    if not ip_address:
        raise ValueError("An IP address is required.")

    connection = get_connection()

    try:
        cursor = connection.cursor()

        # Match by IP because an ARP candidate has no known hostname.
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

            # Do not overwrite an existing verified asset's details.
            # Keep unknown candidates unverified.
            cursor.execute(
                """
                UPDATE dbo.Assets
                SET Status = CASE
                    WHEN Status = 'Active' THEN 'Active'
                    WHEN Status = 'Inactive' THEN 'Inactive'
                    ELSE 'Unverified'
                END
                WHERE AssetID = ?
                """,
                (asset_id,),
            )
        else:
            cursor.execute(
                """
                INSERT INTO dbo.Assets
                    (AssetName, AssetType, IPAddress,
                     OperatingSystem, Status, LastSeen)
                OUTPUT INSERTED.AssetID
                VALUES (?, 'Computer', ?, ?, 'Unverified', NULL)
                """,
                (asset_name, ip_address, operating_system),
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
                   OperatingSystem, Criticality, Status,
                   LastSeen, CreatedAt
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
    """Mark stale, previously active assets as inactive."""
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
