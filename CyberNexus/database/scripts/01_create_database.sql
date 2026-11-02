
USE master;
GO

CREATE DATABASE CyberNexusDB;
GO

SELECT name AS DatabaseName
FROM sys.databases
WHERE name = 'CyberNexusDB';
GO
	