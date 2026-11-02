USE msdb;
GO

SELECT
    database_name AS DatabaseName,
    CASE type
        WHEN 'D' THEN 'Full Backup'
        WHEN 'I' THEN 'Differential Backup'
        WHEN 'L' THEN 'Transaction Log'
        ELSE type
    END AS BackupType,
    backup_start_date AS BackupStartTime,
    backup_finish_date AS BackupFinishTime,
    CASE
        WHEN is_copy_only = 1 THEN 'Copy-only'
        ELSE 'Standard'
    END AS BackupCategory
FROM dbo.backupset
WHERE database_name = 'CyberNexusDB'
ORDER BY backup_finish_date DESC;
GO