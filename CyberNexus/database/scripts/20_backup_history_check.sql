
USE msdb;
GO

SELECT TOP (20)
    bs.database_name AS DatabaseName,
    CASE bs.type
        WHEN 'D' THEN 'Full'
        WHEN 'I' THEN 'Differential'
        WHEN 'L' THEN 'Transaction Log'
        ELSE bs.type
    END AS BackupType,
    bs.backup_start_date AS BackupStartTime,
    bs.backup_finish_date AS BackupFinishTime,
    CAST(bs.backup_size / 1048576.0 AS DECIMAL(10,2))
        AS BackupSizeMB,
    bmf.physical_device_name AS BackupFile
FROM dbo.backupset AS bs
LEFT JOIN dbo.backupmediafamily AS bmf
    ON bs.media_set_id = bmf.media_set_id
WHERE bs.database_name = 'CyberNexusDB'
ORDER BY bs.backup_finish_date DESC;
GO
