
from app.services.database import get_connection


def register_asset(asset: dict) -> dict:
    """Save a discovered asset or update its existing record."""
    connection = get_connection()

    try:
        cursor = connection.cursor()

        hostname = asset.get("hostname")
        ip_address = asset.get("ip_address")
        operating_system = asset.get("operating_system")

        cursor.execute(
            """
            SELECT AssetID
            FROM dbo.Assets
            WHERE AssetName = ?
            """,
            (hostname,),
        )
        existing = cursor.fetchone()

        if existing:
            asset_id = existing[0]
            cursor.execute(
                """
                UPDATE dbo.Assets
                SET IPAddress = ?,
                    OperatingSystem = ?,
                    Status = 'Active',
                    LastSeen = SYSUTCDATETIME()
                WHERE AssetID = ?
                """,
                (ip_address, operating_system, asset_id),
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
    """Mark assets inactive when they have not been seen recently."""
    if timeout_seconds < 1:
        raise ValueError("timeout_seconds must be at least 1")

    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute(
            """
            UPDATE dbo.Assets
            SET Status = 'Inactive'
            WHERE LastSeen IS NULL
               OR LastSeen < DATEADD(
                    SECOND, -?, SYSUTCDATETIME()
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
