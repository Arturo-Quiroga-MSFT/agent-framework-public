-- Diagnostic queries for Azure AD (Entra ID) authentication
-- Run these in Azure Data Studio with Entra ID auth to troubleshoot

-- 1. Check who you're currently logged in as
SELECT 
    SUSER_NAME() AS CurrentUser,
    USER_NAME() AS DatabaseUser,
    SYSTEM_USER AS SystemUser;

-- 2. Check all Azure AD users in the database
SELECT 
    name AS UserName,
    type_desc AS UserType,
    authentication_type_desc AS AuthType,
    create_date,
    modify_date
FROM sys.database_principals
WHERE type IN ('E', 'X')  -- E = External user, X = External group
ORDER BY create_date DESC;

-- 3. Check your current permissions
EXECUTE AS USER = USER_NAME();
SELECT 
    dp.name AS RoleName,
    dp.type_desc AS RoleType
FROM sys.database_role_members drm
JOIN sys.database_principals dp ON drm.role_principal_id = dp.principal_id
WHERE drm.member_principal_id = USER_ID();
REVERT;

-- 4. Check if you have any explicit permissions
SELECT 
    USER_NAME(grantee_principal_id) AS Grantee,
    permission_name,
    state_desc
FROM sys.database_permissions
WHERE grantee_principal_id = USER_ID()
ORDER BY permission_name;

-- 5. Try to query a system view (will fail if no permissions)
SELECT TOP 1 
    name,
    type_desc
FROM sys.tables;
