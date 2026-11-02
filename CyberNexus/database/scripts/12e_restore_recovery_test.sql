USE master;
GO

-- Restore full backup into a fresh test database
RESTORE DATABASE CyberNexusDB_RecoveryTest2
FROM DISK = 'C:\CyberNexus_Backups\CyberNexusDB_Full_Rebuild.bak'
WITH
    MOVE 'CyberNexusDB'
        TO 'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\CyberNexusDB_RecoveryTest2.mdf',
    MOVE 'CyberNexusDB_log'
        TO 'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\CyberNexusDB_RecoveryTest2_log.ldf',
    NORECOVERY,
    CHECKSUM,
    STATS = 10;
GO

-- Apply the differential backup
RESTORE DATABASE CyberNexusDB_RecoveryTest2
FROM DISK = 'C:\CyberNexus_Backups\CyberNexusDB_Differential_Rebuild.bak'
WITH
    RECOVERY,
    CHECKSUM,
    STATS = 10;
GO

-- Check recovery status
SELECT name, state_desc
FROM sys.databases
WHERE name = 'CyberNexusDB_RecoveryTest2';
GO
