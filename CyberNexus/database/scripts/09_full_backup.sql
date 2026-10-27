
USE master;
GO

-- Create a full backup of CyberNexusDB
BACKUP DATABASE CyberNexusDB
TO DISK = 'C:\CyberNexus_Backups\CyberNexusDB_Full_Rebuild.bak'
WITH
    CHECKSUM,
    STATS = 10;
GO
