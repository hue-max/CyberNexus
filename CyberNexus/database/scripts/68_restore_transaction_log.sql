USE master;
GO

RESTORE LOG CyberNexus_LogRecoveryTest
FROM DISK = 'C:\CyberNexus_Backups\CyberNexusDB_Log_Rebuild.trn'
WITH NORECOVERY, STATS = 10;
GO