# Microsoft Entra ID (Azure AD) Authentication Setup

This guide walks you through switching from SQL Authentication to Microsoft Entra ID authentication for the RDBMS Assistant.

## Benefits of Entra ID Authentication

✅ **No Passwords in Config Files** - Credentials managed by Azure  
✅ **Audit Trail** - Track which user performed each action  
✅ **Compliance** - Meets enterprise security policies  
✅ **Automatic Token Refresh** - No expired passwords  
✅ **Multi-Factor Authentication** - Additional security layer  
✅ **Centralized Access Management** - Control via Azure Portal  

---

## Prerequisites

1. **Azure AD Admin Access**: You need to be an Azure AD administrator on the SQL Server
2. **Azure CLI Installed**: Team members need Azure CLI installed and authenticated
3. **SQL Server Entra ID Admin Configured**: Server must have an Azure AD admin set

---

## Step 1: Configure SQL Server Azure AD Admin

### Option A: Using Azure Portal

1. Navigate to [Azure Portal](https://portal.azure.com)
2. Go to **SQL Servers** → Select your server (e.g., `aqsqlserver001`)
3. Click **Microsoft Entra admin** (formerly "Active Directory admin")
4. Click **Set admin**
5. Search for and select an Azure AD user or group as admin
6. Click **Select** and **Save**

### Option B: Using Azure CLI

```bash
# Set Azure AD admin for SQL Server
az sql server ad-admin create \
  --resource-group AI-FOUNDRY-RG \
  --server-name aqsqlserver001 \
  --display-name "Your Name" \
  --object-id $(az ad user show --id your.email@company.com --query id -o tsv)
```

---

## Step 2: Grant Database Access to Users

### Connect as Azure AD Admin

Using Azure Data Studio or SSMS, connect to your database:
- **Server**: `aqsqlserver001.database.windows.net`
- **Authentication**: Azure Active Directory - Universal with MFA
- **Database**: `TERADATA-FI`

### Create Database Users

Run the SQL commands in `setup_entra_id_access.sql`:

```sql
-- For yourself
CREATE USER [your.email@company.com] FROM EXTERNAL PROVIDER;
ALTER ROLE db_owner ADD MEMBER [your.email@company.com];
GO

-- For team members
CREATE USER [team.member@company.com] FROM EXTERNAL PROVIDER;
ALTER ROLE db_owner ADD MEMBER [team.member@company.com];
GO
```

### Verify Users Created

```sql
SELECT 
    name as UserName,
    type_desc as UserType,
    authentication_type_desc as AuthType
FROM sys.database_principals
WHERE type IN ('E', 'X')
ORDER BY name;
```

---

## Step 3: Update Application Configuration

### Update .env File

Edit `DBMS-ASSISTANT/.env`:

```env
# Comment out SQL Authentication credentials
# SQL_USERNAME=
# SQL_PASSWORD=

# Keep these settings
SERVER_NAME=aqsqlserver001.database.windows.net
DATABASE_NAME=TERADATA-FI
TRUST_SERVER_CERTIFICATE=true
READONLY=false
```

The MCP server automatically uses Azure AD when `SQL_USERNAME` and `SQL_PASSWORD` are empty.

---

## Step 4: Team Member Setup

Each team member must:

### 1. Install Azure CLI

**macOS:**
```bash
brew install azure-cli
```

**Windows:**
```powershell
# Download from: https://aka.ms/installazurecliwindows
# Or use winget:
winget install Microsoft.AzureCLI
```

### 2. Login to Azure

```bash
az login
```

This opens a browser for authentication. Sign in with your Azure AD account.

### 3. Verify Authentication

```bash
# Check current account
az account show

# Should show your email and subscription
```

### 4. Launch RDBMS Assistant

The app will now automatically use your Azure AD credentials.

---

## Step 5: Test the Connection

1. Start the Tauri app: `npm run tauri dev`
2. Check the terminal output for: `Using authentication method: Azure AD (Entra ID)`
3. Ask the agent: "List all tables"
4. Verify connection status shows your database

If successful, you should see tables listed without any authentication errors.

---

## Troubleshooting

### Error: "Login failed for user 'NT AUTHORITY\ANONYMOUS LOGON'"

**Cause**: Azure AD user not created in database  
**Fix**: Run the `CREATE USER` commands as shown in Step 2

### Error: "Cannot open server requested by the login"

**Cause**: SQL Server doesn't have Azure AD admin configured  
**Fix**: Complete Step 1 to set Azure AD admin

### Error: "Interactive authentication is required"

**Cause**: Azure CLI not logged in or token expired  
**Fix**: Run `az login` again

### Error: "The token is expired"

**Cause**: Azure CLI token expired (happens after 90 days)  
**Fix**: Run `az login --tenant your-tenant-id` to refresh

### Connection Still Shows "Disconnected"

**Cause**: MCP server can't acquire Azure AD token  
**Fix**: 
1. Verify `az account show` works
2. Check `SQL_USERNAME` is commented out in .env
3. Restart the Tauri app
4. Check terminal logs for error messages

---

## Security Best Practices

### For Production Deployment

1. **Disable Public Access** (after setting up Private Endpoint):
   ```bash
   az sql server update \
     --resource-group AI-FOUNDRY-RG \
     --name aqsqlserver001 \
     --set publicNetworkAccess=Disabled
   ```

2. **Disable SQL Authentication** (Entra ID only):
   ```bash
   az sql server update \
     --resource-group AI-FOUNDRY-RG \
     --name aqsqlserver001 \
     --enable-ad-only-auth
   ```

3. **Use Conditional Access Policies**:
   - Require MFA for database access
   - Restrict access to corporate networks
   - Configure session controls

4. **Enable Auditing**:
   ```sql
   -- Enable Azure SQL auditing
   CREATE DATABASE AUDIT SPECIFICATION [UserAccessAudit]
   FOR SERVER AUDIT [AzureAudit]
   ADD (SCHEMA_OBJECT_ACCESS_GROUP),
   ADD (DATABASE_OBJECT_ACCESS_GROUP)
   WITH (STATE = ON);
   ```

---

## Rollback to SQL Authentication

If you need to revert:

1. Uncomment SQL credentials in `.env`:
   ```env
   SQL_USERNAME=arturoqu
   SQL_PASSWORD=Porkinos.72848677
   ```

2. Restart the app

3. Terminal will show: `Using authentication method: SQL Authentication`

---

## Next Steps

After Entra ID is working:
1. ✅ Remove temporary public access to SQL Server
2. ✅ Set up Azure Private Endpoint for secure access
3. ✅ Distribute the app to team members
4. ✅ Configure audit logging for compliance
5. ✅ Set up monitoring and alerts

---

## References

- [Azure SQL Authentication Methods](https://learn.microsoft.com/azure/azure-sql/database/authentication-aad-overview)
- [Create Azure AD Users in SQL Database](https://learn.microsoft.com/azure/azure-sql/database/authentication-aad-configure)
- [Azure CLI Authentication](https://learn.microsoft.com/cli/azure/authenticate-azure-cli)
- [MSSQL MCP Server Documentation](https://github.com/Azure/mssql-mcp-server)
