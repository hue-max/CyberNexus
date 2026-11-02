
USE master;
GO

/* CyberNexus: Inspect backup chain */

SELECT
    bs.backup_set_id,
    CASE bs.type
        WHEN 'D' THEN 'Full Backup'
        WHEN 'I' THEN 'Differential Backup'
        WHEN 'L' THEN 'Transaction Log Backup'
        ELSE bs.type
    END AS BackupType,
    bs.database_name,
    bs.backup_start_date,
    bs.backup_finish_date,
    bs.first_lsn,
    bs.last_lsn,
    bs.checkpoint_lsn,
    bs.database_backup_lsn,
    bs.differential_base_lsn,
    bs.has_backup_checksums,
    bmf.physical_device_name AS BackupFile
FROM msdb.dbo.backupset AS bs
INNER JOIN msdb.dbo.backupmediafamily AS bmf
    ON bs.media_set_id = bmf.media_set_id
WHERE bs.database_name = 'CyberNexusDB'
ORDER BY bs.backup_finish_date DESC;
GO
