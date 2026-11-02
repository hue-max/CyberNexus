
USE CyberNexusDB;
GO

-- 1. Insert sample assets
INSERT INTO dbo.Assets
    (AssetName, AssetType, IPAddress, OperatingSystem, Criticality)
VALUES
    ('Main-Server', 'Server', '192.168.1.10', 'Windows Server', 'High'),
    ('Workstation-01', 'Workstation', '192.168.1.20', 'Windows 11', 'Medium'),
    ('Linux-Server', 'Server', '192.168.1.30', 'Ubuntu Linux', 'High'),
    ('Test-Device', 'Workstation', '192.168.1.40', 'Windows 10', 'Low');
GO

-- 2. Insert sample security events
INSERT INTO dbo.SecurityEvents
    (AssetID, EventType, Severity, Source, Description)
VALUES
    (1, 'Failed Login', 'Medium', '192.168.1.50',
     'Multiple failed login attempts detected'),
    (2, 'Port Scan', 'High', '192.168.1.60',
     'Suspicious port scanning activity'),
    (3, 'File Modification', 'Low', 'Local Agent',
     'Unexpected configuration file modification'),
    (1, 'Unusual Traffic', 'High', '192.168.1.70',
     'Unusual outbound network traffic detected');
GO

-- 3. Insert sample threats
INSERT INTO dbo.Threats
    (EventID, ThreatType, Confidence, Status)
VALUES
    (1, 'Brute Force Attempt', 92.50, 'Detected'),
    (2, 'Network Reconnaissance', 88.00, 'Detected'),
    (4, 'Suspicious Network Activity', 76.50, 'Investigating');
GO

-- 4. Insert sample risk assessments
INSERT INTO dbo.RiskAssessments
    (AssetID, ThreatID, RiskScore, Explanation)
VALUES
    (1, 1, 85, 'Repeated failed logins indicate high risk'),
    (2, 2, 65, 'Port scanning requires investigation'),
    (1, 3, 75, 'Unusual network activity requires review'),
    (3, NULL, 20, 'Routine monitoring with low current risk');
GO



USE CyberNexusDB;
GO

SELECT COUNT(*) AS TotalAssets FROM dbo.Assets;
SELECT COUNT(*) AS TotalSecurityEvents FROM dbo.SecurityEvents;
SELECT COUNT(*) AS TotalThreats FROM dbo.Threats;
SELECT COUNT(*) AS TotalRiskAssessments FROM dbo.RiskAssessments;
GO
