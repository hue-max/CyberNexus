
USE master;
GO

-- Verify the full backup
RESTORE VERIFYONLY
FROM DISK = 'C:\CyberNexus_Backups\CyberNexusDB_Full_Rebuild.bak'
WITH CHECKSUM;
GO

-- Verify the differential backup
RESTORE VERIFYONLY
FROM DISK = 'C:\CyberNexus_Backups\CyberNexusDB_Differential_Rebuild.bak'
WITH CHECKSUM;
GO
