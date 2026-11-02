SELECT
    bs.backup_set_id,
    CASE bs.type
        WHEN 'D' THEN 'Full'
        WHEN 'I' THEN 'Differential'
        WHEN 'L' THEN 'Transaction Log'
    END AS BackupType,
    bs.backup_start_date,
    bmf.physical_device_name AS BackupFile,
    bs.first_lsn,
    bs.last_lsn,
    bs.database_backup_lsn
FROM msdb.dbo.backupset AS bs
JOIN msdb.dbo.backupmediafamily AS bmf
    ON bs.media_set_id = bmf.media_set_id
WHERE bs.database_name = 'CyberNexusDB'
ORDER BY bs.backup_start_date DESC;
GO