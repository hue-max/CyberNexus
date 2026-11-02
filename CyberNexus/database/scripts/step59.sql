SELECT TOP 5
    j.name AS JobName,
    msdb.dbo.agent_datetime(h.run_date, h.run_time) AS RunDateTime,
    h.run_status,
    h.message
FROM msdb.dbo.sysjobhistory h
JOIN msdb.dbo.sysjobs j
    ON h.job_id = j.job_id
WHERE j.name = 'CyberNexus_Daily_Full_Backup'
  AND h.step_id = 0
ORDER BY h.instance_id DESC;
GO