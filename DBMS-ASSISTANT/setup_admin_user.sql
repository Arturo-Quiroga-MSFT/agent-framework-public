-- Create database user for admin@MngEnvMCAP094150.onmicrosoft.com
-- Run this in Azure Data Studio connected to TERADATA-FI with Entra ID authentication

USE [TERADATA-FI];
GO

-- Create the external user from Azure AD
CREATE USER [admin@MngEnvMCAP094150.onmicrosoft.com] FROM EXTERNAL PROVIDER;
GO

-- Grant db_owner role for full database permissions
ALTER ROLE db_owner ADD MEMBER [admin@MngEnvMCAP094150.onmicrosoft.com];
GO

-- Verify the user was created successfully
SELECT 
    name AS UserName,
    type_desc AS UserType,
    authentication_type_desc AS AuthType,
    create_date
FROM sys.database_principals
WHERE name = 'admin@MngEnvMCAP094150.onmicrosoft.com';
GO

-- Check the user's roles
SELECT 
    dp.name AS RoleName
FROM sys.database_role_members drm
JOIN sys.database_principals dp ON drm.role_principal_id = dp.principal_id
WHERE USER_NAME(drm.member_principal_id) = 'admin@MngEnvMCAP094150.onmicrosoft.com';
GO
