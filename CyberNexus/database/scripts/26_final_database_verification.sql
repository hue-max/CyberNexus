USE CyberNexusDB;
GO

-- Check database status
SELECT
    name AS DatabaseName,
    state_desc AS DatabaseStatus,
    recovery_model_desc AS RecoveryModel
FROM sys.databases
WHERE name = 'CyberNexusDB';
GO

-- Check all four main tables
SELECT
    t.name AS TableName,
    SUM(p.rows) AS TotalRows
FROM sys.tables t
JOIN sys.partitions p
    ON t.object_id = p.object_id
WHERE p.index_id IN (0, 1)
GROUP BY t.name
ORDER BY t.name;
GO

-- Check database integrity
DBCC CHECKDB ('CyberNexusDB')
WITH NO_INFOMSGS;
GO