SELECT
    name AS DatabaseName,
    state_desc AS Status,
    recovery_model_desc AS RecoveryModel
FROM sys.databases
WHERE name IN (
    'CyberNexusDB',
    'CyberNexus_LogRecoveryTest'
);
GO