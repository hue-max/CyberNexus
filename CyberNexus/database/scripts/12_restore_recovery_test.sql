
USE master;
GO

-- Restore the full backup using a new test database name
RESTORE DATABASE CyberNexusDB_RecoveryTest
FROM DISK = 'C:\CyberNexus_Backups\CyberNexusDB_Full_Rebuild.bak'
WITH
    MOVE 'CyberNexusDB'
        TO 'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\CyberNexusDB_RecoveryTest.mdf',
    MOVE 'CyberNexusDB_log'
        TO 'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\CyberNexusDB_RecoveryTest_log.ldf',
    NORECOVERY,
    CHECKSUM,
    STATS = 10;
GO

-- Apply the differential backup
RESTORE DATABASE CyberNexusDB_RecoveryTest
FROM DISK = 'C:\CyberNexus_Backups\CyberNexusDB_Differential_Rebuild.bak'
WITH
    RECOVERY,
    CHECKSUM,
    STATS = 10;
GO

-- Verify that the restored database is online
SELECT name, state_desc
FROM sys.databases
WHERE name = 'CyberNexusDB_RecoveryTest';
GO

-- Check restored table data
USE CyberNexusDB_RecoveryTest;
GO

SELECT 'Assets' AS TableName, COUNT_BIG(*) AS TotalRows
FROM dbo.Assets
UNION ALL
SELECT 'SecurityEvents', COUNT_BIG(*) FROM dbo.SecurityEvents
UNION ALL
SELECT 'Threats', COUNT_BIG(*) FROM dbo.Threats
UNION ALL
SELECT 'RiskAssessments', COUNT_BIG(*) FROM dbo.RiskAssessments;
GO

RESTORE FILELISTONLY
FROM DISK = 'C:\CyberNexus_Backups\CyberNexusDB_Full_Rebuild.bak';
GO