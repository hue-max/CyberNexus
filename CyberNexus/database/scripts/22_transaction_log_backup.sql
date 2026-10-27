	
USE master;
GO

BACKUP LOG CyberNexusDB
TO DISK = 'C:\CyberNexus_Backups\CyberNexusDB_Log_Rebuild.trn'
WITH CHECKSUM, STATS = 10;
GO
