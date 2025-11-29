-- ============================================================
-- STEP 1: Discover actual column names in fact and dimension tables
-- Run this first to see what columns exist
-- ============================================================

-- Check all columns in fact tables
SELECT 
    'FACT_TABLE' AS TableType,
    t.TABLE_NAME,
    c.COLUMN_NAME,
    c.DATA_TYPE,
    c.IS_NULLABLE,
    CASE 
        WHEN c.COLUMN_NAME LIKE '%Key' THEN 'LIKELY_FK'
        WHEN c.COLUMN_NAME LIKE '%ID' THEN 'LIKELY_FK'
        ELSE 'DATA'
    END AS ColumnPurpose
FROM INFORMATION_SCHEMA.TABLES t
INNER JOIN INFORMATION_SCHEMA.COLUMNS c 
    ON t.TABLE_NAME = c.TABLE_NAME 
    AND t.TABLE_SCHEMA = c.TABLE_SCHEMA
WHERE t.TABLE_SCHEMA = 'fact'
ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION;

-- Check all key columns in dimension tables
SELECT 
    'DIM_TABLE' AS TableType,
    t.TABLE_NAME,
    c.COLUMN_NAME,
    c.DATA_TYPE,
    c.IS_NULLABLE,
    CASE 
        WHEN c.ORDINAL_POSITION = 1 THEN 'LIKELY_PK'
        ELSE 'ATTRIBUTE'
    END AS ColumnPurpose
FROM INFORMATION_SCHEMA.TABLES t
INNER JOIN INFORMATION_SCHEMA.COLUMNS c 
    ON t.TABLE_NAME = c.TABLE_NAME 
    AND t.TABLE_SCHEMA = c.TABLE_SCHEMA
WHERE t.TABLE_SCHEMA = 'dim'
ORDER BY t.TABLE_NAME, c.ORDINAL_POSITION;

-- Check existing primary keys
SELECT 
    SCHEMA_NAME(t.schema_id) AS SchemaName,
    t.name AS TableName,
    tc.name AS ConstraintName,
    c.name AS ColumnName
FROM sys.key_constraints tc
INNER JOIN sys.tables t ON tc.parent_object_id = t.object_id
INNER JOIN sys.index_columns ic ON tc.parent_object_id = ic.object_id AND tc.unique_index_id = ic.index_id
INNER JOIN sys.columns c ON ic.object_id = c.object_id AND ic.column_id = c.column_id
WHERE tc.type = 'PK'
    AND SCHEMA_NAME(t.schema_id) IN ('dim', 'fact')
ORDER BY SchemaName, TableName;

-- Check existing foreign keys
SELECT 
    fk.name AS ForeignKeyName,
    OBJECT_SCHEMA_NAME(fk.parent_object_id) AS TableSchema,
    OBJECT_NAME(fk.parent_object_id) AS TableName,
    COL_NAME(fc.parent_object_id, fc.parent_column_id) AS ColumnName,
    OBJECT_SCHEMA_NAME(fk.referenced_object_id) AS ReferencedSchema,
    OBJECT_NAME(fk.referenced_object_id) AS ReferencedTable,
    COL_NAME(fc.referenced_object_id, fc.referenced_column_id) AS ReferencedColumn
FROM sys.foreign_keys AS fk
INNER JOIN sys.foreign_key_columns AS fc 
    ON fk.object_id = fc.constraint_object_id
WHERE OBJECT_SCHEMA_NAME(fk.parent_object_id) IN ('dim', 'fact')
ORDER BY TableSchema, TableName;
