DECLARE @DataPath NVARCHAR(4000);
DECLARE @LogPath NVARCHAR(4000);

SET @DataPath =
    CAST(SERVERPROPERTY('InstanceDefaultDataPath') AS NVARCHAR(4000));

SET @LogPath =
    CAST(SERVERPROPERTY('InstanceDefaultLogPath') AS NVARCHAR(4000));

PRINT 'DATA PATH: ' + ISNULL(@DataPath, 'Not configured');
PRINT 'LOG PATH: ' + ISNULL(@LogPath, 'Not configured');
GO