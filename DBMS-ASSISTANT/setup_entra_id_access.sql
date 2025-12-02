-- ============================================================================
-- Setup Microsoft Entra ID (Azure AD) Authentication for RDBMS Assistant
-- ============================================================================
-- Run these commands as an Azure AD admin user on your Azure SQL Database

-- Step 1: Create a database user for your Azure AD account
-- Replace 'user@yourdomain.com' with your Azure AD email
CREATE USER [user@yourdomain.com] FROM EXTERNAL PROVIDER;
GO

-- Step 2: Grant appropriate permissions
-- For DBA operations, grant db_owner (full control)
ALTER ROLE db_owner ADD MEMBER [user@yourdomain.com];
GO

-- OR for more granular control, grant specific roles:
-- ALTER ROLE db_datareader ADD MEMBER [user@yourdomain.com];  -- Read data
-- ALTER ROLE db_datawriter ADD MEMBER [user@yourdomain.com];  -- Write data
-- ALTER ROLE db_ddladmin ADD MEMBER [user@yourdomain.com];    -- DDL operations (CREATE TABLE, ALTER, etc.)
-- GRANT VIEW DEFINITION TO [user@yourdomain.com];             -- View metadata

-- Step 3 (Optional): Create users for other team members
-- CREATE USER [team.member@yourdomain.com] FROM EXTERNAL PROVIDER;
-- ALTER ROLE db_owner ADD MEMBER [team.member@yourdomain.com];
-- GO

-- Step 4: Verify user creation
SELECT 
    name as UserName,
    type_desc as UserType,
    authentication_type_desc as AuthType
FROM sys.database_principals
WHERE type IN ('E', 'X')  -- E = External User, X = External Group
ORDER BY name;
GO

-- ============================================================================
-- Azure Portal Configuration (must be done by SQL Server admin)
-- ============================================================================
-- 1. Navigate to Azure Portal > SQL Server > Settings > Microsoft Entra admin
-- 2. Set an Azure AD admin for the SQL Server (if not already set)
-- 3. Connect to the database using that admin account
-- 4. Run the CREATE USER commands above
-- 5. Disable public network access (optional, for security)
-- 6. Disable SQL Authentication (optional, enforce Entra ID only)
