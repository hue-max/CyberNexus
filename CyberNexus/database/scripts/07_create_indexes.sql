
USE CyberNexusDB;
GO

-- 1. Find security events by asset
CREATE NONCLUSTERED INDEX IX_SecurityEvents_AssetID
ON dbo.SecurityEvents (AssetID);
GO

-- 2. Find events by severity and time
CREATE NONCLUSTERED INDEX IX_SecurityEvents_Severity_EventTimestamp
ON dbo.SecurityEvents (Severity, EventTimestamp DESC);
GO

-- 3. Find threats by related event
CREATE NONCLUSTERED INDEX IX_Threats_EventID
ON dbo.Threats (EventID);
GO

-- 4. Find risk assessments by asset
CREATE NONCLUSTERED INDEX IX_RiskAssessments_AssetID
ON dbo.RiskAssessments (AssetID);
GO

-- 5. Find risk assessments by score
CREATE NONCLUSTERED INDEX IX_RiskAssessments_RiskScore
ON dbo.RiskAssessments (RiskScore DESC);
GO

-- Verify the indexes
SELECT
    OBJECT_NAME(object_id) AS TableName,
    name AS IndexName,
    type_desc AS IndexType
FROM sys.indexes
WHERE name IN (
    'IX_SecurityEvents_AssetID',
    'IX_SecurityEvents_Severity_EventTimestamp',
    'IX_Threats_EventID',
    'IX_RiskAssessments_AssetID',
    'IX_RiskAssessments_RiskScore'
)
ORDER BY TableName, IndexName;
GO
