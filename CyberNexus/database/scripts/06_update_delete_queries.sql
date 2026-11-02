
USE CyberNexusDB;
GO

-- 1. Update an asset's status
UPDATE dbo.Assets
SET Status = 'Active'
WHERE AssetName = 'Main-Server';
GO

-- Verify the update
SELECT AssetID, AssetName, Status
FROM dbo.Assets
WHERE AssetName = 'Main-Server';
GO

-- 2. Update a security event's severity
UPDATE dbo.SecurityEvents
SET Severity = 'High'
WHERE EventID = 1;
GO

-- Verify the update
SELECT EventID, EventType, Severity
FROM dbo.SecurityEvents
WHERE EventID = 1;
GO

-- 3. Update a threat's status
UPDATE dbo.Threats
SET Status = 'Investigating'
WHERE ThreatID = 1;
GO

-- Verify the update
SELECT ThreatID, ThreatType, Status
FROM dbo.Threats
WHERE ThreatID = 1;
GO

-- 4. SAFE DELETE EXAMPLE
-- Preview the test record first
SELECT *
FROM dbo.Assets
WHERE AssetName = 'Test-Device';
GO

-- Uncomment the DELETE below only when you intentionally
-- want to remove this test asset and it has no related events.
-- DELETE FROM dbo.Assets
-- WHERE AssetName = 'Test-Device';
-- GO
