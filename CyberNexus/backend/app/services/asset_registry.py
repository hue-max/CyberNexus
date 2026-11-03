
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
            cursor.execute(
                """
                UPDATE dbo.Assets
                SET IPAddress = ?,
                    OperatingSystem = ?,
                    Status = 'Active',
                    LastSeen = SYSUTCDATETIME()
                WHERE AssetID = ?
                """,
                (ip_address, operating_system, existing[0]),
            )
            asset_id = existing[0]
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
