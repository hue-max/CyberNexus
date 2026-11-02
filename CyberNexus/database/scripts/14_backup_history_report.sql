
USE msdb;
GO

-- View backup history for CyberNexusDB
SELECT
    database_name AS DatabaseName,
    CASE type
        WHEN 'D' THEN 'Full Backup'
        WHEN 'I' THEN 'Differential Backup'
        WHEN 'L' THEN 'Transaction Log Backup'
        ELSE type
    END AS BackupType,
    backup_start_date AS BackupStartTime,
    backup_finish_date AS BackupFinishTime,
    CAST(backup_size / 1048576.0 AS DECIMAL(10,2))
        AS BackupSizeMB,
    physical_device_name AS BackupFile
FROM dbo.backupset AS bs
INNER JOIN dbo.backupmediafamily AS bmf
    ON bs.media_set_id = bmf.media_set_id
WHERE database_name = 'CyberNexusDB'
ORDER BY backup_finish_date DESC;
GO
