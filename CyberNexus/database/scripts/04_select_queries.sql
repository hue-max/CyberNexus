
USE CyberNexusDB;
GO

-- 1. Display all assets
SELECT *
FROM dbo.Assets;
GO

-- 2. Display all security events
SELECT *
FROM dbo.SecurityEvents;
GO

-- 3. Display all detected threats
SELECT *
FROM dbo.Threats;
GO

-- 4. Display all risk assessments
SELECT *
FROM dbo.RiskAssessments;
GO

-- 5. Find high-criticality assets
SELECT AssetID, AssetName, IPAddress, Criticality
FROM dbo.Assets
WHERE Criticality = 'High';
GO

-- 6. Find high-severity security events
SELECT EventID, EventType, Severity, Source, Description
FROM dbo.SecurityEvents
WHERE Severity = 'High';
GO

-- 7. Find threats with confidence above 80%
SELECT ThreatID, ThreatType, Confidence, Status
FROM dbo.Threats
WHERE Confidence > 80;
GO

-- 8. Find high-risk assessments (score above 80)
SELECT RiskAssessmentID, AssetID, ThreatID, RiskScore, Explanation
FROM dbo.RiskAssessments
WHERE RiskScore > 80;
GO

-- 9. Sort assets by criticality and name
SELECT AssetID, AssetName, Criticality, Status
FROM dbo.Assets
ORDER BY
    CASE Criticality
        WHEN 'High' THEN 1
        WHEN 'Medium' THEN 2
        WHEN 'Low' THEN 3
        ELSE 4
    END,
    AssetName;
GO

-- 10. Display the five latest security events
SELECT TOP (5) *
FROM dbo.SecurityEvents
ORDER BY EventTimestamp DESC, EventID DESC;
GO
