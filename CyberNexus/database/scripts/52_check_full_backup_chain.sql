SELECT
    backup_set_id,
    type,
    backup_start_date,
    first_lsn,
    last_lsn,
    checkpoint_lsn,
    database_backup_lsn,
    differential_base_lsn
FROM msdb.dbo.backupset
WHERE database_name = 'CyberNexusDB'
  AND type IN ('D', 'I', 'L')
ORDER BY backup_start_date;
GO