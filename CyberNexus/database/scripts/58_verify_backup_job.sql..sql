SELECT
    name,
    enabled,
    date_created
FROM msdb.dbo.sysjobs
WHERE name = 'CyberNexus_Daily_Full_Backup';
GO