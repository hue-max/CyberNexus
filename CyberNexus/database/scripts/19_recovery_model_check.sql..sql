
USE master;
GO

SELECT
    name AS DatabaseName,
    recovery_model_desc AS RecoveryModel,
    log_reuse_wait_desc AS LogReuseWait
FROM sys.databases
WHERE name IN (
    'CyberNexusDB',
    'CyberNexusDB_RecoveryTest',
    'CyberNexusDB_RecoveryTest2'
);
GO
