
USE master;
GO

-- Create a differential backup
BACKUP DATABASE CyberNexusDB
TO DISK = 'C:\CyberNexus_Backups\CyberNexusDB_Differential_Rebuild.bak'
WITH
    DIFFERENTIAL,
    CHECKSUM,
    STATS = 10;
GO
