
USE CyberNexusDB_RecoveryTest2;
GO

SELECT 'Assets' AS TableName, COUNT_BIG(*) AS TotalRows
FROM dbo.Assets
UNION ALL
SELECT 'SecurityEvents', COUNT_BIG(*) FROM dbo.SecurityEvents
UNION ALL
SELECT 'Threats', COUNT_BIG(*) FROM dbo.Threats
UNION ALL
SELECT 'RiskAssessments', COUNT_BIG(*) FROM dbo.RiskAssessments;
GO

-- View recovered assets
SELECT * FROM dbo.Assets;
GO

-- View recovered security events
SELECT * FROM dbo.SecurityEvents;
GO
