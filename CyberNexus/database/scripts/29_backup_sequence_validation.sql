
USE master;
GO

/* CyberNexus: Inspect latest backup metadata */

SELECT
    backup_set_id,
    type AS BackupTypeCode,
    backup_start_date,
    backup_finish_date,
    first_lsn,
    last_lsn,
    checkpoint_lsn,
    database_backup_lsn,
    differential_base_lsn,
    is_copy_only
FROM msdb.dbo.backupset
WHERE database_name = 'CyberNexusDB'
  AND type IN ('D', 'I', 'L')
ORDER BY backup_finish_date DESC;
GO
