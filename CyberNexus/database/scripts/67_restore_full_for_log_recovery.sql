USE master;
GO

RESTORE DATABASE CyberNexus_LogRecoveryTest
FROM DISK = 'C:\CyberNexus_Backups\CyberNexusDB_Full_Rebuild.bak'
WITH
    FILE = 2,
    MOVE 'CyberNexusDB'
        TO 'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\CyberNexus_LogRecoveryTest.mdf',
    MOVE 'CyberNexusDB_log'
        TO 'C:\Program Files\Microsoft SQL Server\MSSQL16.MSSQLSERVER\MSSQL\DATA\CyberNexus_LogRecoveryTest_log.ldf',
    NORECOVERY,
    STATS = 10;
GO