
USE msdb;
GO

SELECT
    backup_set_id AS BackupSetID,
    CASE type
        WHEN 'D' THEN 'Full'
        WHEN 'I' THEN 'Differential'
        WHEN 'L' THEN 'Transaction Log'
    END AS BackupType,
    backup_start_date AS BackupStartTime,
    backup_finish_date AS BackupFinishTime,
    first_lsn AS FirstLSN,
    last_lsn AS LastLSN,
    checkpoint_lsn AS CheckpointLSN,
    database_backup_lsn AS DatabaseBackupLSN
FROM dbo.backupset
WHERE database_name = 'CyberNexusDB'
ORDER BY backup_finish_date;
GO
