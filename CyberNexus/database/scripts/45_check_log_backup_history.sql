SELECT
    backup_set_id,
    type,
    backup_start_date,
    backup_finish_date,
    first_lsn,
    last_lsn,
    checkpoint_lsn,
    database_backup_lsn,
    differential_base_lsn
FROM msdb.dbo.backupset
WHERE database_name = 'CyberNexusDB'
ORDER BY backup_finish_date;
GO