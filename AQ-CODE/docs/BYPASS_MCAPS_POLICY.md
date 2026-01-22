# Bypassing MCAPS "Disable Local Auth" Policy

**Issue:** Unable to enable key-based authentication on Cognitive Services and Storage Accounts due to MCAPS policy enforcement.

**Error Message:**
```
{"error":{"code":"BadRequest","message":"Failed to list key. disableLocalAuth is set to be true"}}
```

**Policy:** "Disable Local auth for all Cognitive Services"

---

## 🔑 Solution: Apply SecurityControl Tag at RESOURCE Level

### ⚠️ Critical Detail

**The tag MUST be applied at the RESOURCE level, NOT the Resource Group level.**

Many PSAs were trying to apply the tag at the RG level, which doesn't work for this policy exemption.

---

## 📝 Step-by-Step Instructions

### Step 1: Add SecurityControl Tag to the Resource

#### For Cognitive Services (Document Intelligence, OpenAI, etc.)

```bash
# Get your subscription ID first
SUBSCRIPTION_ID=$(az account show --query id -o tsv)

# Apply tag to Cognitive Services resource
az tag create \
  --resource-id "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/YOUR-RG-NAME/providers/Microsoft.CognitiveServices/accounts/YOUR-RESOURCE-NAME" \
  --tags SecurityControl=Ignore
```

**Example (Document Intelligence):**
```bash
az tag create \
  --resource-id "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/AQ-FOUNDRY-RG/providers/Microsoft.CognitiveServices/accounts/AQ-DOC-INTEL" \
  --tags SecurityControl=Ignore
```

#### For Storage Accounts

```bash
# Apply tag to Storage Account resource
az tag create \
  --resource-id "/subscriptions/$SUBSCRIPTION_ID/resourceGroups/YOUR-RG-NAME/providers/Microsoft.Storage/storageAccounts/YOUR-STORAGE-NAME" \
  --tags SecurityControl=Ignore
```

**Example:**
```bash
az tag create \
  --resource-id "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/AQ-FOUNDRY-RG/providers/Microsoft.Storage/storageAccounts/staqmainhub339573983327" \
  --tags SecurityControl=Ignore
```

---

### Step 2: Enable Key-Based Authentication

#### For Cognitive Services

```bash
# Set disableLocalAuth to false
az resource update \
  --name YOUR-RESOURCE-NAME \
  --resource-group YOUR-RG-NAME \
  --resource-type "Microsoft.CognitiveServices/accounts" \
  --set properties.disableLocalAuth=false
```

**Example:**
```bash
az resource update \
  --name AQ-DOC-INTEL \
  --resource-group AQ-FOUNDRY-RG \
  --resource-type "Microsoft.CognitiveServices/accounts" \
  --set properties.disableLocalAuth=false
```

#### For Storage Accounts

```bash
# Enable shared key access
az storage account update \
  --name YOUR-STORAGE-NAME \
  --resource-group YOUR-RG-NAME \
  --allow-shared-key-access true
```

**Example:**
```bash
az storage account update \
  --name staqmainhub339573983327 \
  --resource-group AQ-FOUNDRY-RG \
  --allow-shared-key-access true
```

---

### Step 3: Verify the Changes

#### Verify Cognitive Services

```bash
# Check disableLocalAuth status and tags
az resource show \
  --name YOUR-RESOURCE-NAME \
  --resource-group YOUR-RG-NAME \
  --resource-type "Microsoft.CognitiveServices/accounts" \
  --query "{disableLocalAuth: properties.disableLocalAuth, tags: tags}"
```

**Expected output:**
```
DisableLocalAuth    Tags
------------------  ---------------------------
False               {'SecurityControl': 'Ignore'}
```

#### Verify Storage Account

```bash
# Check allowSharedKeyAccess status
az storage account show \
  --name YOUR-STORAGE-NAME \
  --query "{name: name, allowSharedKeyAccess: allowSharedKeyAccess, tags: tags}"
```

**Expected output:**
```json
{
  "allowSharedKeyAccess": true,
  "name": "staqmainhub339573983327",
  "tags": {
    "SecurityControl": "Ignore"
  }
}
```

---

## 🎯 Complete Working Examples

### Example 1: Document Intelligence Resource

```bash
# 1. Add tag
az tag create \
  --resource-id "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/AQ-FOUNDRY-RG/providers/Microsoft.CognitiveServices/accounts/AQ-DOC-INTEL" \
  --tags SecurityControl=Ignore

# 2. Enable key access
az resource update \
  --name AQ-DOC-INTEL \
  --resource-group AQ-FOUNDRY-RG \
  --resource-type "Microsoft.CognitiveServices/accounts" \
  --set properties.disableLocalAuth=false

# 3. Verify
az resource show \
  --name AQ-DOC-INTEL \
  --resource-group AQ-FOUNDRY-RG \
  --resource-type "Microsoft.CognitiveServices/accounts" \
  --query "properties.disableLocalAuth"
# Output: False ✅
```

### Example 2: Storage Account

```bash
# 1. Add tag
az tag create \
  --resource-id "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/AQ-FOUNDRY-RG/providers/Microsoft.Storage/storageAccounts/staqmainhub339573983327" \
  --tags SecurityControl=Ignore

# 2. Enable shared key access
az storage account update \
  --name staqmainhub339573983327 \
  --resource-group AQ-FOUNDRY-RG \
  --allow-shared-key-access true

# 3. Verify
az storage account show \
  --name staqmainhub339573983327 \
  --query "allowSharedKeyAccess"
# Output: true ✅
```

---

## 🚨 Common Mistakes

### ❌ Mistake 1: Applying Tag at Resource Group Level

```bash
# This DOES NOT WORK for this policy
az tag create \
  --resource-id "/subscriptions/$SUB_ID/resourceGroups/YOUR-RG" \
  --tags SecurityControl=Ignore
```

**Why it fails:** The MCAPS policy checks tags at the resource level, not the RG level.

---

### ❌ Mistake 2: Wrong Tag Value

```bash
# Wrong values that don't work:
--tags SecurityControl=Exempt
--tags SecurityControl=Allow
--tags SecurityControl=Bypass
```

**Correct value:** Must be exactly `SecurityControl=Ignore` (case-sensitive)

---

### ❌ Mistake 3: Trying to Enable Auth Before Adding Tag

```bash
# This will fail if policy is active
az resource update \
  --name YOUR-RESOURCE \
  --resource-group YOUR-RG \
  --resource-type "Microsoft.CognitiveServices/accounts" \
  --set properties.disableLocalAuth=false
```

**Error:**
```
Policy restriction prevents this operation
```

**Fix:** Add the tag FIRST, then enable authentication.

---

## 🔍 Troubleshooting

### Issue: Tag Added But Still Can't Enable Key Access

**Check 1: Verify tag is on the resource**
```bash
az resource show \
  --name YOUR-RESOURCE \
  --resource-group YOUR-RG \
  --resource-type "Microsoft.CognitiveServices/accounts" \
  --query "tags"
```

**Check 2: Wait for policy propagation**
Sometimes policy evaluation takes 5-10 minutes. Wait and retry.

**Check 3: Verify exact tag name and value**
```bash
# Must be exactly this:
SecurityControl=Ignore
# NOT:
security-control=ignore
SecurityControl=ignore  # lowercase
```

---

### Issue: Can't Find Resource ID

**Get full resource ID:**
```bash
# For Cognitive Services
az cognitiveservices account show \
  --name YOUR-RESOURCE \
  --resource-group YOUR-RG \
  --query "id" -o tsv

# For Storage Accounts
az storage account show \
  --name YOUR-STORAGE \
  --query "id" -o tsv
```

---

## 📋 Quick Reference Commands

### Find All Cognitive Services in Subscription

```bash
az cognitiveservices account list \
  --query "[].{name: name, rg: resourceGroup, localAuth: properties.disableLocalAuth}" \
  -o table
```

### Find All Storage Accounts in Subscription

```bash
az storage account list \
  --query "[].{name: name, rg: resourceGroup, keyAccess: allowSharedKeyAccess}" \
  -o table
```

### Bulk Apply Tags (Multiple Resources)

```bash
# For all Cognitive Services in a resource group
for resource in $(az cognitiveservices account list --resource-group YOUR-RG --query "[].name" -o tsv); do
  echo "Tagging $resource..."
  az tag create \
    --resource-id "/subscriptions/$(az account show --query id -o tsv)/resourceGroups/YOUR-RG/providers/Microsoft.CognitiveServices/accounts/$resource" \
    --tags SecurityControl=Ignore
done
```

---

## 🎓 Key Learnings

1. **Resource-level tags** are required for MCAPS policy exemptions
2. **Exact tag name/value** matters: `SecurityControl=Ignore`
3. **Order matters**: Add tag BEFORE enabling key access
4. **Verification** is critical: Always check that changes took effect
5. **Policy propagation** can take a few minutes

---

## 💡 Why This Works

The MCAPS policy has an exemption condition that checks for the `SecurityControl=Ignore` tag at the **resource level**. When this tag is present:

1. The policy allows the resource to opt-out of the "disable local auth" requirement
2. You can then manually set `disableLocalAuth=false` or `allowSharedKeyAccess=true`
3. The resource can use key-based authentication

### 📖 Official Microsoft Documentation Support

According to Microsoft's Azure Policy documentation, policy exemptions and tag-based conditions are **evaluated at the specific resource level**, not inherited from resource groups:

> **"The exemption object is created on the resource hierarchy or individual resource as a child object, which determines the scope of the exemption."**  
> *Source: [Azure Policy exemption structure](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/exemption-structure)*

Key points from Microsoft documentation:

1. **Resource-Level Evaluation**: 
   - Azure Policy evaluates tags **on the specific resource being assessed**
   - Tags on resource groups are NOT automatically evaluated for resources within that group
   - *Reference: [Azure Policy Scope](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/scope)*

2. **Tag Inheritance vs. Tag Evaluation**:
   - While Azure supports *inheriting* tag values from resource groups using `resourceGroup()` function in policies, this is **explicit behavior in the policy definition itself**
   - The MCAPS "Disable Local Auth" policy does NOT have this inheritance logic
   - It only checks tags **directly on the resource**
   - *Reference: [Azure Policy pattern: tags](https://learn.microsoft.com/en-us/azure/governance/policy/samples/pattern-tags)*

3. **Exemption Scope**:
   - Policy exemptions must target **"the resource hierarchy or individual resource"**
   - The exemption determines its scope based on where it's created
   - *Reference: [Azure Policy exemption structure - Scope](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/exemption-structure)*

### Why Resource Group Tags Don't Work

When you apply the `SecurityControl=Ignore` tag at the **Resource Group level**:

```bash
# This doesn't work ❌
az tag create \
  --resource-id "/subscriptions/.../resourceGroups/YOUR-RG" \
  --tags SecurityControl=Ignore
```

**What happens:**
1. The tag is added to the **Resource Group object** only
2. When the policy evaluates a **Cognitive Services or Storage resource**, it checks that resource's tags
3. The resource doesn't have the tag (it's on the parent RG)
4. Policy enforcement continues → key access remains disabled

**The fix:**
```bash
# This works ✅
az tag create \
  --resource-id "/subscriptions/.../resourceGroups/YOUR-RG/providers/Microsoft.CognitiveServices/accounts/YOUR-RESOURCE" \
  --tags SecurityControl=Ignore
```

Now the policy evaluates the **resource's own tags** and finds `SecurityControl=Ignore`, allowing the exemption.

---

## 📞 Credit

Thanks to **George Bittencourt** for the SecurityControl tag solution documented in the Teams thread with Nikki Conley (Jan 20, 2026).

---

## ⚠️ Security Note

**Use this exemption responsibly:**
- Only apply to resources that genuinely need key-based access
- Consider using Managed Identity where possible
- Document why key access is required
- Rotate keys regularly
- Monitor key usage via Azure Monitor

---

## 📚 Official Microsoft Documentation References

### Azure Policy Core Concepts
- **[Azure Policy exemption structure](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/exemption-structure)** - Details on how exemptions work at resource level
- **[Azure Policy Scope](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/scope)** - Explains resource vs. resource group evaluation
- **[Azure Policy pattern: tags](https://learn.microsoft.com/en-us/azure/governance/policy/samples/pattern-tags)** - How tag conditions are evaluated in policies

### Authentication & Security
- **[Cognitive Services Authentication](https://learn.microsoft.com/azure/cognitive-services/authentication)** - Best practices for Cognitive Services auth
- **[Storage Account Security](https://learn.microsoft.com/azure/storage/common/authorize-data-access)** - Storage account authentication methods
- **[Managed Identity Best Practices](https://learn.microsoft.com/azure/active-directory/managed-identities-azure-resources/overview)** - Preferred alternative to key-based auth

### Tag Management
- **[Assign policy definitions for tag compliance](https://learn.microsoft.com/en-us/azure/azure-resource-manager/management/tag-policies)** - Tag policy examples
- **[Use tags to organize your Azure resources](https://learn.microsoft.com/azure/azure-resource-manager/management/tag-resources)** - Tag management fundamentals

---

**Last Updated:** January 22, 2026  
**Tested On:** Azure CLI 2.x, Document Intelligence, Storage Accounts  
**Status:** ✅ Verified Working
