
SELECT
    'DataFolder: ' +
    CAST(SERVERPROPERTY('InstanceDefaultDataPath') AS NVARCHAR(4000))
UNION ALL
SELECT
    'LogFolder: ' +
    CAST(SERVERPROPERTY('InstanceDefaultLogPath') AS NVARCHAR(4000));
GO
