
USE CyberNexusDB;
GO

-- 1. Inspect all four tables
EXEC sp_help 'dbo.Assets';
EXEC sp_help 'dbo.SecurityEvents';
EXEC sp_help 'dbo.Threats';
EXEC sp_help 'dbo.RiskAssessments';
GO

-- 2. Inspect indexes
SELECT
    OBJECT_NAME(i.object_id) AS TableName,
    i.name AS IndexName,
    i.type_desc AS IndexType,
    i.is_primary_key AS IsPrimaryKey,
    i.is_unique AS IsUnique
FROM sys.indexes AS i
WHERE i.object_id IN (
    OBJECT_ID('dbo.Assets'),
    OBJECT_ID('dbo.SecurityEvents'),
    OBJECT_ID('dbo.Threats'),
    OBJECT_ID('dbo.RiskAssessments')
)
ORDER BY TableName, IndexName;
GO

-- 3. Inspect foreign keys
SELECT
    OBJECT_NAME(parent_object_id) AS TableName,
    name AS ForeignKeyName,
    OBJECT_NAME(referenced_object_id) AS ReferencedTable
FROM sys.foreign_keys
WHERE parent_object_id IN (
    OBJECT_ID('dbo.Assets'),
    OBJECT_ID('dbo.SecurityEvents'),
    OBJECT_ID('dbo.Threats'),
    OBJECT_ID('dbo.RiskAssessments')
)
ORDER BY TableName, ForeignKeyName;
GO

USE CyberNexusDB;
GO

-- All indexes on the four CyberNexus tables
SELECT
    OBJECT_NAME(i.object_id) AS TableName,
    i.name AS IndexName,
    i.type_desc AS IndexType
FROM sys.indexes AS i
WHERE i.object_id IN
(
    OBJECT_ID('dbo.Assets'),
    OBJECT_ID('dbo.SecurityEvents'),
    OBJECT_ID('dbo.Threats'),
    OBJECT_ID('dbo.RiskAssessments')
)
AND i.name IS NOT NULL
ORDER BY TableName, IndexName;
GO

-- All foreign-key relationships
SELECT
    OBJECT_NAME(fk.parent_object_id) AS ChildTable,
    COL_NAME(fkc.parent_object_id, fkc.parent_column_id) AS ChildColumn,
    OBJECT_NAME(fk.referenced_object_id) AS ParentTable,
    COL_NAME(fkc.referenced_object_id, fkc.referenced_column_id) AS ParentColumn
FROM sys.foreign_keys AS fk
INNER JOIN sys.foreign_key_columns AS fkc
    ON fk.object_id = fkc.constraint_object_id
ORDER BY ChildTable, ChildColumn;
GO