
USE master;
GO

/* Compare full backup and differential backup bases */

SELECT
    backup_set_id,
    CASE type
        WHEN 'D' THEN 'Full'
        WHEN 'I' THEN 'Differential'
        WHEN 'L' THEN 'Transaction Log'
    END AS BackupType,
    backup_start_date,
    checkpoint_lsn,
    database_backup_lsn,
    differential_base_lsn,
    differential_base_guid
FROM msdb.dbo.backupset
WHERE database_name = 'CyberNexusDB'
  AND backup_set_id IN (4, 5, 6, 7, 8)
ORDER BY backup_set_id;
GO
