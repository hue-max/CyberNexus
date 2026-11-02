SELECT
    name,
    state_desc
FROM sys.databases
WHERE name IN (
    'CyberNexusDB',
    'CyberNexusDB_RecoveryTest',
    'CyberNexusDB_RecoveryTest2'
);
GO