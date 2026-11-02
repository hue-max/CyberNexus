
USE master;
GO

SELECT
    bs.backup_set_id AS BackupID,
    CASE bs.type
        WHEN 'D' THEN 'Full'
        WHEN 'I' THEN 'Differential'
        WHEN 'L' THEN 'Transaction Log'
    END AS BackupType,
    bmf.physical_device_name AS BackupFilePath
FROM msdb.dbo.backupset AS bs
INNER JOIN msdb.dbo.backupmediafamily AS bmf
    ON bs.media_set_id = bmf.media_set_id
WHERE bs.database_name = 'CyberNexusDB'
  AND bs.backup_set_id IN (4, 5, 6, 7, 8)
ORDER BY bs.backup_set_id;
GO
