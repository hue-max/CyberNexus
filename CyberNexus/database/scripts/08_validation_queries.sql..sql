
USE CyberNexusDB;
GO

-- 1. Check row counts
SELECT 'Assets' AS TableName, COUNT_BIG(*) AS TotalRows
FROM dbo.Assets
UNION ALL
SELECT 'SecurityEvents', COUNT_BIG(*) FROM dbo.SecurityEvents
UNION ALL
SELECT 'Threats', COUNT_BIG(*) FROM dbo.Threats
UNION ALL
SELECT 'RiskAssessments', COUNT_BIG(*) FROM dbo.RiskAssessments;
GO

-- 2. Check risk scores outside the valid range
SELECT *
FROM dbo.RiskAssessments
WHERE RiskScore > 100;
GO

-- 3. Check invalid threat confidence values
SELECT *
FROM dbo.Threats
WHERE Confidence < 0 OR Confidence > 100;
GO

-- 4. Check events referencing missing assets
SELECT E.EventID, E.AssetID, E.EventType
FROM dbo.SecurityEvents AS E
LEFT JOIN dbo.Assets AS A ON E.AssetID = A.AssetID
WHERE E.AssetID IS NOT NULL
  AND A.AssetID IS NULL;
GO

-- 5. Check threats referencing missing events
SELECT T.ThreatID, T.EventID
FROM dbo.Threats AS T
LEFT JOIN dbo.SecurityEvents AS E ON T.EventID = E.EventID
WHERE E.EventID IS NULL;
GO

-- 6. Check risk assessments referencing missing records
SELECT R.RiskAssessmentID
FROM dbo.RiskAssessments AS R
LEFT JOIN dbo.Assets AS A ON R.AssetID = A.AssetID
LEFT JOIN dbo.Threats AS T ON R.ThreatID = T.ThreatID
WHERE (R.AssetID IS NOT NULL AND A.AssetID IS NULL)
   OR (R.ThreatID IS NOT NULL AND T.ThreatID IS NULL);
GO
