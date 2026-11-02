SELECT
    name AS DatabaseName,
    state_desc AS Status
FROM sys.databases
WHERE name IN (
    'CyberNexusDB',
    'CyberNexusDB_RecoveryTest',
    'CyberNexusDB_RecoveryTest2'
);
GO