
USE CyberNexusDB;
GO

-- 1. Security events with asset details
SELECT
    A.AssetName,
    A.IPAddress,
    E.EventID,
    E.EventType,
    E.Severity,
    E.Source,
    E.Description,
    E.EventTimestamp
FROM dbo.SecurityEvents AS E
LEFT JOIN dbo.Assets AS A
    ON E.AssetID = A.AssetID
ORDER BY E.EventID;
GO

-- 2. Threats with their related security events
SELECT
    T.ThreatID,
    T.ThreatType,
    T.Confidence,
    T.Status AS ThreatStatus,
    E.EventType,
    E.Severity,
    E.Source
FROM dbo.Threats AS T
INNER JOIN dbo.SecurityEvents AS E
    ON T.EventID = E.EventID
ORDER BY T.ThreatID;
GO

-- 3. Risk assessments with asset and threat details
SELECT
    R.RiskAssessmentID,
    A.AssetName,
    T.ThreatType,
    R.RiskScore,
    R.Explanation,
    R.AssessmentTime
FROM dbo.RiskAssessments AS R
LEFT JOIN dbo.Assets AS A
    ON R.AssetID = A.AssetID
LEFT JOIN dbo.Threats AS T
    ON R.ThreatID = T.ThreatID
ORDER BY R.RiskScore DESC;
GO

-- 4. Complete security overview
SELECT
    A.AssetName,
    E.EventType,
    E.Severity,
    T.ThreatType,
    T.Confidence,
    R.RiskScore,
    R.Explanation
FROM dbo.SecurityEvents AS E
LEFT JOIN dbo.Assets AS A
    ON E.AssetID = A.AssetID
LEFT JOIN dbo.Threats AS T
    ON T.EventID = E.EventID
LEFT JOIN dbo.RiskAssessments AS R
    ON R.ThreatID = T.ThreatID
    OR (R.ThreatID IS NULL AND R.AssetID = A.AssetID)
ORDER BY R.RiskScore DESC, E.EventID;
GO
