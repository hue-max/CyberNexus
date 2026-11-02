
USE master;
GO

/* CyberNexus: Verify full, differential,
   and transaction-log backup files */

RESTORE VERIFYONLY
FROM DISK = 'C:\CyberNexus_Backups\CyberNexusDB_Full_Rebuild.bak'
WITH CHECKSUM;
GO

RESTORE VERIFYONLY
FROM DISK = 'C:\CyberNexus_Backups\CyberNexusDB_Differential_Rebuild.bak'
WITH CHECKSUM;
GO

RESTORE VERIFYONLY
FROM DISK = 'C:\CyberNexus_Backups\CyberNexusDB_Log_Rebuild.trn'
WITH CHECKSUM;
GO
