USE master;
GO

SELECT name, state_desc, user_access_desc
FROM sys.databases
WHERE name = 'CyberNexusDB_RecoveryTest';
GO	
