
USE CyberNexusDB;
GO

-- 1. Assets
CREATE TABLE dbo.Assets (
    AssetID INT IDENTITY(1,1) PRIMARY KEY,
    AssetName NVARCHAR(100) NOT NULL,
    AssetType NVARCHAR(50),
    IPAddress VARCHAR(45),
    OperatingSystem NVARCHAR(100),
    Criticality NVARCHAR(20) NOT NULL
        DEFAULT 'Medium',
    Status NVARCHAR(20) NOT NULL
        DEFAULT 'Active',
    LastSeen DATETIME2 NULL,
    CreatedAt DATETIME2 NOT NULL
        DEFAULT SYSUTCDATETIME()
);
GO

-- 2. Security Events
CREATE TABLE dbo.SecurityEvents (
    EventID BIGINT IDENTITY(1,1) PRIMARY KEY,
    AssetID INT NULL,
    EventType NVARCHAR(100) NOT NULL,
    Severity NVARCHAR(20) NOT NULL,
    Source NVARCHAR(100),
    Description NVARCHAR(500),
    EventTimestamp DATETIME2 NOT NULL
        DEFAULT SYSUTCDATETIME(),
    ReceivedTimestamp DATETIME2 NOT NULL
        DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_SecurityEvents_Assets
        FOREIGN KEY (AssetID)
        REFERENCES dbo.Assets(AssetID)
);
GO

-- 3. Threats
CREATE TABLE dbo.Threats (
    ThreatID BIGINT IDENTITY(1,1) PRIMARY KEY,
    EventID BIGINT NOT NULL,
    ThreatType NVARCHAR(100) NOT NULL,
    Confidence DECIMAL(5,2),
    Status NVARCHAR(30) NOT NULL
        DEFAULT 'Detected',
    DetectedAt DATETIME2 NOT NULL
        DEFAULT SYSUTCDATETIME(),

    CONSTRAINT FK_Threats_SecurityEvents
        FOREIGN KEY (EventID)
        REFERENCES dbo.SecurityEvents(EventID),

    CONSTRAINT CK_Threats_Confidence
        CHECK (Confidence IS NULL OR
               Confidence BETWEEN 0 AND 100)
);
GO

-- 4. Risk Assessments
CREATE TABLE dbo.RiskAssessments (
    RiskAssessmentID BIGINT IDENTITY(1,1) PRIMARY KEY,
    AssetID INT NULL,
    ThreatID BIGINT NULL,
    RiskScore TINYINT NOT NULL,
    AssessmentTime DATETIME2 NOT NULL
        DEFAULT SYSUTCDATETIME(),
    Explanation NVARCHAR(500),

    CONSTRAINT FK_RiskAssessments_Assets
        FOREIGN KEY (AssetID)
        REFERENCES dbo.Assets(AssetID),

    CONSTRAINT FK_RiskAssessments_Threats
        FOREIGN KEY (ThreatID)
        REFERENCES dbo.Threats(ThreatID),

    CONSTRAINT CK_RiskAssessments_RiskScore
        CHECK (RiskScore BETWEEN 0 AND 100),

    CONSTRAINT CK_RiskAssessments_Reference
        CHECK (AssetID IS NOT NULL OR ThreatID IS NOT NULL)
);
GO



USE CyberNexusDB;
GO

SELECT TABLE_NAME
FROM INFORMATION_SCHEMA.TABLES
WHERE TABLE_TYPE = 'BASE TABLE'
ORDER BY TABLE_NAME;
GO
