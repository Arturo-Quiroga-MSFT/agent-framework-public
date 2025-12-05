# Complete Agent Identity Mapping

**Generated**: December 4, 2025  
**Project**: aq-ai-foundry-Sweden-Central-firstProject  
**Total Agents**: 9

## Agent Name → Object ID Mapping

| Agent Name | Object ID | Version | Created |
|------------|-----------|---------|---------|
| **WebSearchAgent** | `38c14420-a914-4370-a0f8-1b014598c1d0` | 7 | 2025-12-04, 11:42 AM |
| **BasicWeatherAgent** | `966ccc07-512a-4698-bafb-4d5686973d27` | 10 | 2025-12-04, 11:39 AM |
| **ResearchAgent** | `9350dda6-b732-4b1c-a111-c5d8c4ffc64a` | 3 | 2025-12-04, 11:38 AM |
| **DataAnalysisAgent** | `a3be091d-da7b-4696-b0f6-b7f41f5cca84` | 2 | 2025-12-04, 09:02 AM |
| **CodeInterpreterAgent** | `d73547cc-9f5f-4de5-8f3b-97e14f882016` | 3 | 2025-12-03, 02:38 PM |
| **FileSearchAgent** | `0e1584e6-f309-4e4b-9909-3200e3bca7a5` | 2 | 2025-12-03, 02:35 PM |
| **BasicAgent** | `bde46d80-de73-4bd9-9416-4515799ae72d` | 3 | 2025-12-03, 02:34 PM |
| **WeatherAgent** | `ff55957a-bbf1-4be8-9e41-0046b2b2494c` | 1 | 2025-11-24, 10:12 AM |
| **BingGroundingAgent** | `420c8552-5d64-4c44-869c-037ad07ef351` | 1 | 2025-11-23, 03:29 PM |

---

## RBAC Assignment Commands

Use these commands to grant Azure resource permissions to your agents:

### Storage Access Example

```bash
# WebSearchAgent - Storage Blob Data Reader
az role assignment create \
  --assignee 38c14420-a914-4370-a0f8-1b014598c1d0 \
  --role "Storage Blob Data Reader" \
  --scope /subscriptions/<SUB_ID>/resourceGroups/<RG>/providers/Microsoft.Storage/storageAccounts/<ACCOUNT>

# BasicWeatherAgent - Storage Blob Data Reader
az role assignment create \
  --assignee 966ccc07-512a-4698-bafb-4d5686973d27 \
  --role "Storage Blob Data Reader" \
  --scope /subscriptions/<SUB_ID>/resourceGroups/<RG>/providers/Microsoft.Storage/storageAccounts/<ACCOUNT>

# ResearchAgent - Storage Blob Data Reader
az role assignment create \
  --assignee 9350dda6-b732-4b1c-a111-c5d8c4ffc64a \
  --role "Storage Blob Data Reader" \
  --scope /subscriptions/<SUB_ID>/resourceGroups/<RG>/providers/Microsoft.Storage/storageAccounts/<ACCOUNT>

# DataAnalysisAgent - Storage Blob Data Contributor
az role assignment create \
  --assignee a3be091d-da7b-4696-b0f6-b7f41f5cca84 \
  --role "Storage Blob Data Contributor" \
  --scope /subscriptions/<SUB_ID>/resourceGroups/<RG>/providers/Microsoft.Storage/storageAccounts/<ACCOUNT>

# CodeInterpreterAgent - Storage Blob Data Contributor
az role assignment create \
  --assignee d73547cc-9f5f-4de5-8f3b-97e14f882016 \
  --role "Storage Blob Data Contributor" \
  --scope /subscriptions/<SUB_ID>/resourceGroups/<RG>/providers/Microsoft.Storage/storageAccounts/<ACCOUNT>

# FileSearchAgent - Storage Blob Data Reader
az role assignment create \
  --assignee 0e1584e6-f309-4e4b-9909-3200e3bca7a5 \
  --role "Storage Blob Data Reader" \
  --scope /subscriptions/<SUB_ID>/resourceGroups/<RG>/providers/Microsoft.Storage/storageAccounts/<ACCOUNT>

# BasicAgent - Storage Blob Data Reader
az role assignment create \
  --assignee bde46d80-de73-4bd9-9416-4515799ae72d \
  --role "Storage Blob Data Reader" \
  --scope /subscriptions/<SUB_ID>/resourceGroups/<RG>/providers/Microsoft.Storage/storageAccounts/<ACCOUNT>

# WeatherAgent - Storage Blob Data Reader
az role assignment create \
  --assignee ff55957a-bbf1-4be8-9e41-0046b2b2494c \
  --role "Storage Blob Data Reader" \
  --scope /subscriptions/<SUB_ID>/resourceGroups/<RG>/providers/Microsoft.Storage/storageAccounts/<ACCOUNT>

# BingGroundingAgent - Storage Blob Data Reader
az role assignment create \
  --assignee 420c8552-5d64-4c44-869c-037ad07ef351 \
  --role "Storage Blob Data Reader" \
  --scope /subscriptions/<SUB_ID>/resourceGroups/<RG>/providers/Microsoft.Storage/storageAccounts/<ACCOUNT>
```

### Cosmos DB Access Example

```bash
# DataAnalysisAgent - Cosmos DB Built-in Data Contributor
az cosmosdb sql role assignment create \
  --account-name <COSMOSDB_ACCOUNT> \
  --resource-group <RG> \
  --role-definition-name "Cosmos DB Built-in Data Contributor" \
  --principal-id a3be091d-da7b-4696-b0f6-b7f41f5cca84 \
  --scope "/"
```

### Key Vault Access Example

```bash
# All Agents - Key Vault Secrets User
for AGENT_ID in 38c14420-a914-4370-a0f8-1b014598c1d0 966ccc07-512a-4698-bafb-4d5686973d27 9350dda6-b732-4b1c-a111-c5d8c4ffc64a a3be091d-da7b-4696-b0f6-b7f41f5cca84 d73547cc-9f5f-4de5-8f3b-97e14f882016 0e1584e6-f309-4e4b-9909-3200e3bca7a5 bde46d80-de73-4bd9-9416-4515799ae72d ff55957a-bbf1-4be8-9e41-0046b2b2494c 420c8552-5d64-4c44-869c-037ad07ef351; do
  az role assignment create \
    --assignee $AGENT_ID \
    --role "Key Vault Secrets User" \
    --scope /subscriptions/<SUB_ID>/resourceGroups/<RG>/providers/Microsoft.KeyVault/vaults/<VAULT_NAME>
done
```

---

## Adding Custom Attributes in Entra ID

To make agents easier to identify in the Entra ID portal:

1. Go to **Entra ID** → **Agent ID** → **All agent identities**
2. Search for an Object ID (e.g., `38c14420-a914-4370-a0f8-1b014598c1d0`)
3. Click on the agent
4. Go to **Custom security attributes (Preview)**
5. Add attributes:
   - **AgentName**: WebSearchAgent
   - **Purpose**: Web search and information retrieval
   - **Environment**: Production
   - **Owner**: your-team@company.com

---

## Quick Search Reference

To find a specific agent in Entra ID portal, search for these Object IDs:

- **WebSearchAgent**: Search `38c14420`
- **BasicWeatherAgent**: Search `966ccc07`
- **ResearchAgent**: Search `9350dda6`
- **DataAnalysisAgent**: Search `a3be091d`
- **CodeInterpreterAgent**: Search `d73547cc`
- **FileSearchAgent**: Search `0e1584e6`
- **BasicAgent**: Search `bde46d80`
- **WeatherAgent**: Search `ff55957a`
- **BingGroundingAgent**: Search `420c8552`

---

## Next Steps

1. ✅ **Assign RBAC permissions** using commands above
2. ✅ **Add custom attributes** in Entra ID for better identification
3. ✅ **Configure MCP tools** to use agent identity authentication
4. ✅ **Set up conditional access policies** for risk-based control
5. ✅ **Enable audit logging** to monitor agent activities
6. ✅ **Create alerts** for suspicious agent behavior

---

**Files**:
- JSON mapping: `agent_identity_mapping_complete.json`
- This reference: `AGENT_IDENTITY_REFERENCE.md`
