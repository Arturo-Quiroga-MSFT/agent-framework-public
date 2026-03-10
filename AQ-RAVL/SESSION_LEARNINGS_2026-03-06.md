---
title: "Session Learnings: FOCUS Export Research and Azure Subscription Testing"
description: "Findings from the March 6, 2026 research session covering FOCUS export capabilities, Azure subscription types, CLI limitations, and sample data acquisition"
author: Arturo Quiroga
ms.date: 2026-03-06
ms.topic: reference
---

## Session Context

On March 6, 2026, a research session was conducted to prepare for the Ravl (Canada) PSA engagement. The goal was to understand Azure Cost Management FOCUS exports, test export creation programmatically, and gather reference data for the FinOps engagement with IGM.

## Key Findings

### 1. FOCUS Export Availability by Agreement Type

Not all Azure subscription types support FOCUS exports. This was discovered when attempting to create a FOCUS export on an MSDN subscription.

| Agreement Type | FOCUS Export | Usage Export | Actual/Amortized |
|---|---|---|---|
| Enterprise Agreement (EA) | Yes | Yes | Yes |
| Microsoft Customer Agreement (MCA, direct) | Yes | Yes | Yes |
| MCA Enterprise | Yes | Yes | Yes |
| Microsoft Partner Agreement (MPA) | Yes | Yes | Yes |
| MSDN / Visual Studio | **No** | Yes | No |
| Microsoft Internal (MCAPS) | **No** | No (no billing access) | No |
| Pay-As-You-Go | Unknown (not tested) | Yes | Unknown |

This matters for the Ravl engagement because IGM must be on EA, MCA, or MPA to use FOCUS exports. Confirming their agreement type is the first question for the discovery call.

### 2. Identifying Azure Subscription Type via CLI

The subscription type is revealed by the `quotaId` field in subscription policies:

```bash
az rest --method get \
  --url "https://management.azure.com/subscriptions/$(az account show --query id -o tsv)?api-version=2022-12-01" \
  --query "{displayName:displayName, subscriptionId:subscriptionId, subscriptionPolicies:subscriptionPolicies}" \
  -o json
```

Common `quotaId` values:

| quotaId | Subscription Type |
|---|---|
| `Internal_2014-09-01` | Microsoft Internal (FTE MCAPS managed) |
| `MSDN_2014-09-01` | Visual Studio / MSDN |
| `PayAsYouGo_2014-09-01` | Pay-As-You-Go |
| `EnterpriseAgreement_2014-09-01` | Enterprise Agreement |
| `MCAIndividual_2014-09-01` | Microsoft Customer Agreement |
| `MSDNDevTest_2014-09-01` | Dev/Test |

### 3. MCAPS Internal Subscriptions Cannot Access Billing

The FTE-managed subscription `ARTURO-MngEnvMCAP094150` (quotaId: `Internal_2014-09-01`) has no access to:

- Billing profile invoices (portal shows "you don't have access to this billing profile")
- Cost Management exports of any type
- FOCUS, actual, or amortized cost data

This subscription is billed to "Microsoft Shadow IT - MCAPS" billing profile, which is centrally managed. It is not suitable for testing any Cost Management export workflows.

### 4. CLI Extension Does Not Support FocusCost Type

The `az costmanagement` CLI extension (installed on demand) only accepts three export types:

```
Valid values: Usage, ActualCost, AmortizedCost
```

`FocusCost` is not recognized by the extension. To create FOCUS exports programmatically, the REST API must be used directly via `az rest`.

### 5. REST API Version Matters for FOCUS

When using the REST API, the export type `FocusCost` is only valid on subscriptions that support it (EA, MCA, MPA). On an MSDN subscription, even the correct API version returns:

```
Invalid definition type 'FocusCost'; valid values: 'Usage'.
```

The API versions tested:

| API Version | FocusCost Support |
|---|---|
| `2023-08-01` | Yes (on EA/MCA/MPA only) |
| `2023-11-01` | Yes (on EA/MCA/MPA only) |
| `2024-08-01` | Yes (on EA/MCA/MPA only) |

The rejection is subscription-level, not API-version-level. All versions return the same error on unsupported subscription types.

### 6. Resource Provider Registration Required

Before creating any Cost Management export, the `Microsoft.CostManagementExports` resource provider must be registered on the subscription:

```bash
az provider register --namespace Microsoft.CostManagementExports
```

Registration takes approximately 15-25 seconds. Without it, the REST API returns:

```
RP Not Registered. Register destination storage account subscription with Microsoft.CostManagementExports.
```

### 7. Usage Export on MSDN Works as Alternative

A native `Usage` export was successfully created on the MSDN subscription via REST API:

```bash
az rest --method put \
  --url "https://management.azure.com/subscriptions/{sub-id}/providers/Microsoft.CostManagement/exports/usage-export-test?api-version=2023-08-01" \
  --body '{
    "properties": {
      "schedule": { "status": "Active", "recurrence": "Daily", ... },
      "format": "Csv",
      "deliveryInfo": {
        "destination": {
          "resourceId": "/subscriptions/{sub-id}/resourceGroups/{rg}/providers/Microsoft.Storage/storageAccounts/{sa}",
          "container": "cost-exports",
          "rootFolderPath": "usage-data"
        }
      },
      "definition": { "type": "Usage", "timeframe": "MonthToDate" }
    }
  }'
```

An immediate run was triggered via:

```bash
az rest --method post \
  --url "https://management.azure.com/subscriptions/{sub-id}/providers/Microsoft.CostManagement/exports/usage-export-test/run?api-version=2023-08-01"
```

The export completed in approximately 12 seconds and produced a CSV with 6 rows of March 2026 usage data.

### 8. Native Usage Export Schema (24 Columns)

The MSDN Usage export contains these columns:

| # | Column | Maps to FOCUS |
|---|---|---|
| 1 | `SubscriptionGuid` | `SubAccountId` |
| 2 | `ResourceGroup` | `x_ResourceGroupName` |
| 3 | `ResourceLocation` | `RegionName` (requires cleansing) |
| 4 | `UsageDateTime` | `ChargePeriodStart` |
| 5 | `MeterCategory` | `x_SkuMeterCategory` |
| 6 | `MeterSubcategory` | `x_SkuMeterSubcategory` |
| 7 | `MeterId` | `x_SkuMeterId` |
| 8 | `MeterName` | `SkuMeter` |
| 9 | `MeterRegion` | `x_SkuRegion` |
| 10 | `UsageQuantity` | `ConsumedQuantity` |
| 11 | `ResourceRate` | `x_BilledUnitPrice` |
| 12 | `PreTaxCost` | `BilledCost` |
| 13 | `ConsumedService` | Used with ResourceType to derive `ServiceName` |
| 14 | `ResourceType` | Used with ConsumedService to derive `ServiceName` |
| 15 | `InstanceId` | `ResourceId` |
| 16 | `Tags` | `Tags` (may need JSON wrapping) |
| 17 | `OfferId` | `x_SkuOfferId` |
| 18 | `AdditionalInfo` | `SkuPriceDetails` |
| 19 | `ServiceInfo1` | (no direct FOCUS mapping) |
| 20 | `ServiceInfo2` | (no direct FOCUS mapping) |
| 21 | `ServiceName` | (not the same as FOCUS ServiceName) |
| 22 | `ServiceTier` | `x_SkuTier` |
| 23 | `Currency` | `BillingCurrency` |
| 24 | `UnitOfMeasure` | `PricingUnit` (via PricingUnits lookup) |

### 9. FOCUS Open Data Lookup Files

The FinOps toolkit provides four CSV files for converting native Cost Management data to FOCUS format. These were downloaded to `focus-sample-data/`:

| File | Rows | Purpose |
|---|---|---|
| `Services.csv` | 398 | Maps `ConsumedService` + `ResourceType` to `ServiceName`, `ServiceCategory`, `ServiceSubcategory` |
| `ResourceTypes.csv` | 2,014 | Maps ARM resource types to friendly display names (`ResourceType` in FOCUS) |
| `Regions.csv` | 501 | Normalizes region strings to consistent `RegionId` and `RegionName` |
| `PricingUnits.csv` | 383 | Maps `UnitOfMeasure` to `PricingUnit` with `PricingBlockSize` for block pricing |

Example mapping from our export data: `ConsumedService: Microsoft.Storage` + `ResourceType: Microsoft.Storage/storageAccounts` resolves to `ServiceName: Storage Accounts` / `ServiceCategory: Storage` in the Services.csv lookup.

### 10. Storage Account Access Requires RBAC or Key Auth

When downloading blobs from the export storage account, `--auth-mode login` failed with a permissions error. The logged-in identity did not have `Storage Blob Data Reader` (or higher) role assigned. Using `--auth-mode key` (which queries for the account key via ARM) worked as a fallback. For production scenarios with Ravl, recommend assigning proper RBAC roles rather than relying on key-based auth.

## Artifacts Created

| Artifact | Path | Description |
|---|---|---|
| Engagement README | `AQ-RAVL/README.md` | Partner engagement overview, key topics, next steps |
| FOCUS Primer | `AQ-RAVL/FOCUS_PRIMER.md` | Comprehensive reference: schema, exports, mapping, gotchas, discovery checklist |
| MSDN Usage Export | `AQ-RAVL/focus-sample-data/msdn-usage-export.csv` | 6 rows of real March 2026 usage data from MSDN subscription |
| Services Lookup | `AQ-RAVL/focus-sample-data/Services.csv` | FinOps toolkit: ConsumedService/ResourceType to FOCUS ServiceName mapping |
| Resource Types Lookup | `AQ-RAVL/focus-sample-data/ResourceTypes.csv` | FinOps toolkit: ARM resource type to friendly display name mapping |
| Regions Lookup | `AQ-RAVL/focus-sample-data/Regions.csv` | FinOps toolkit: region string normalization |
| Pricing Units Lookup | `AQ-RAVL/focus-sample-data/PricingUnits.csv` | FinOps toolkit: UnitOfMeasure to PricingUnit with block sizes |

## Azure Resources Created

| Resource | Subscription | Details |
|---|---|---|
| Cost Management Export: `usage-export-test` | MSDNSUB (`6aa612ef-5168-4a19-8e7c-db14c9849d3a`) | Daily Usage export, writes to `r2dastorageeastus2/cost-exports/usage-data/` |
| Resource Provider: `Microsoft.CostManagementExports` | MSDNSUB | Registered to enable export delivery |

## Implications for the Ravl Engagement

1. **Agreement type is the gating question.** If IGM is not on EA, MCA, or MPA, FOCUS exports are not available. The engagement would then focus on converting native exports to FOCUS format using the open data lookup files.

2. **CLI tooling lags behind the REST API.** When helping the partner set up exports programmatically, use `az rest` with the Cost Management REST API rather than the `az costmanagement` extension, which does not support `FocusCost`.

3. **The native-to-FOCUS column mapping is well documented.** Even without a native FOCUS export, the conversion path is clear using the four open data CSV files from the FinOps toolkit. This could be a useful deliverable for Ravl if they need to support both formats during a transition.

4. **Provider registration is easy to miss.** `Microsoft.CostManagementExports` must be registered before the first export. This should be included in any setup guidance provided to the partner.

5. **Storage RBAC should be planned.** The export service writes to the storage account using its own identity, but consumers of the data (analysts, pipelines) need `Storage Blob Data Reader` at minimum. Include this in the setup checklist for Ravl.
