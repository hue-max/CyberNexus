
USE msdb;
GO

SELECT TOP (1)
    bs.database_name AS DatabaseName,
    bs.backup_start_date AS BackupStartTime,
    bs.backup_finish_date AS BackupFinishTime,
    bs.is_copy_only AS IsCopyOnly,
    bs.has_backup_checksums AS HasBackupChecksums,
    bmf.physical_device_name AS BackupFile
FROM dbo.backupset AS bs
LEFT JOIN dbo.backupmediafamily AS bmf
    ON bs.media_set_id = bmf.media_set_id
WHERE bs.database_name = 'CyberNexusDB'
  AND bs.type = 'D'
ORDER BY bs.backup_finish_date DESC;
GO
