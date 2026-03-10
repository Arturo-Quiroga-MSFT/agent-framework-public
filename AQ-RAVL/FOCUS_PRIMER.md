---
title: "FOCUS Primer for Ravl FinOps Engagement"
description: "Azure Cost Management FOCUS format primer covering exports, schema, tooling, gotchas, and discovery questions for the Ravl/IGM FinOps engagement"
author: Arturo Quiroga
ms.date: 2026-03-06
ms.topic: reference
---

## What Is FOCUS

The FinOps Open Cost and Usage Specification (FOCUS) is a provider-agnostic, open-source billing data format maintained by the FinOps Foundation. It standardizes how cloud cost and usage data is structured, making it easier to allocate, analyze, monitor, and optimize spending across providers.

Azure Cost Management natively supports FOCUS as an export type. When selected, it combines actual (billed) and amortized (effective) costs into a single dataset, resulting in approximately 30% less data than running both actual and amortized exports separately.

## Setting Up FOCUS Exports in Azure

### Prerequisites

- An active Enterprise Agreement (EA), Microsoft Customer Agreement (MCA), or Microsoft Partner Agreement (MPA)
- Appropriate role: Enterprise Admin (EA), Billing Account Owner/Contributor (MCA), or Global Admin/Admin Agent (MPA)
- An Azure Storage account to receive the exported data

### Steps

1. Navigate to **Cost Management + Billing** in the Azure portal.
2. Select the appropriate scope (enrollment, billing profile, subscription, or resource group).
3. Select **Exports** under Settings.
4. Select **Add** to create a new export.
5. Under **Data type**, choose **Cost and usage details (FOCUS)**.
6. Configure the schedule: one-time, daily (month-to-date), or monthly (last month).
7. Specify the target Azure Storage account, container, and directory.
8. Select **Create**.

The management group scope is **not supported** for FOCUS exports.

### Frequency Options

| Schedule | Description |
|---|---|
| One-time export | Single snapshot for a specified date range |
| Daily export of month-to-date costs | Runs daily, accumulating the current month |
| Monthly export of last month's costs | Runs once after billing period closes |

### Export via REST API

Use the [Exports REST API](https://learn.microsoft.com/en-us/rest/api/cost-management/exports) for programmatic export creation. Set `ExportType` to `FocusCost`.

## FOCUS Schema Overview

FOCUS v1.2-preview includes 53 standard columns and 52 Microsoft extension columns (prefixed with `x_`). The standard columns fall into six categories.

### Billing and Invoice

| Column | Description |
|---|---|
| `BillingAccountId` | Unique ID for the billing account (EA enrollment or MCA billing profile) |
| `BillingAccountName` | Display name for the billing account |
| `BillingCurrency` | Currency used for all prices and costs |
| `BillingPeriodStart` | Inclusive start date of the billing period |
| `BillingPeriodEnd` | Exclusive end date of the billing period |
| `InvoiceId` | Invoice identifier (MCA only, not available for EA) |
| `InvoiceIssuerName` | Entity responsible for invoicing |
| `SubAccountId` | Maps to the Azure subscription ID |
| `SubAccountName` | Maps to the Azure subscription name |

### Resource Details

| Column | Description |
|---|---|
| `ResourceId` | Fully qualified Azure Resource Manager ID |
| `ResourceName` | Display name of the resource |
| `ResourceType` | Friendly label for the kind of resource |
| `RegionId` | Provider-assigned region identifier |
| `RegionName` | Cleansed region name, consistent with ARM |
| `ServiceName` | Grouped service name (for example, "Virtual Machines") |
| `ServiceCategory` | High-level category (Compute, Storage, Networking, Databases) |
| `Tags` | Key-value pairs in consistent JSON format |

### Charge Details

| Column | Description |
|---|---|
| `ChargeCategory` | Usage, Purchase, or Adjustment |
| `ChargeClass` | Identifies corrections to prior invoices |
| `ChargeDescription` | Human-readable summary of the charge |
| `ChargeFrequency` | One-time, recurring, or usage-based |
| `ChargePeriodStart` | Inclusive start date of the charge |
| `ChargePeriodEnd` | Exclusive end date of the charge |
| `ConsumedQuantity` | Volume consumed in discrete units |
| `ConsumedUnit` | Measurement unit for consumed quantity |

### Pricing and Cost

| Column | Description |
|---|---|
| `ListUnitPrice` | Public retail price per pricing unit (no discounts) |
| `ListCost` | ListUnitPrice multiplied by PricingQuantity |
| `ContractedUnitPrice` | After negotiated discounts, before commitment discounts |
| `ContractedCost` | ContractedUnitPrice multiplied by PricingQuantity |
| `EffectiveCost` | Amortized cost after all discounts and prepaid purchases |
| `BilledCost` | What was or will be invoiced (actual cost) |
| `PricingQuantity` | Volume based on pricing unit (may differ from consumed) |
| `PricingUnit` | How the provider rates usage after pricing rules |
| `PricingCategory` | On-demand, commitment-based, dynamic, or other |

### Commitment Discounts

| Column | Description |
|---|---|
| `CommitmentDiscountId` | ID of the reservation or savings plan applied |
| `CommitmentDiscountName` | Display name of the commitment discount |
| `CommitmentDiscountCategory` | Usage-based or spend-based |
| `CommitmentDiscountType` | Provider-specific label (for example, Reservation, SavingsPlan) |
| `CommitmentDiscountStatus` | Used or Unused |

### SKU Details

| Column | Description |
|---|---|
| `SkuId` | Identifies the product SKU used |
| `SkuPriceId` | Unique price-point including tiering and discounts |
| `SkuMeter` | Name of the usage meter |
| `ProviderName` | Cloud provider (Microsoft) |
| `PublisherName` | Entity that produced the resource or service |

## Mapping from Native Cost Management to FOCUS

For teams migrating from actual/amortized exports, the key mappings are:

| Native Column | FOCUS Column | Notes |
|---|---|---|
| `CostInBillingCurrency` | `BilledCost` | Actual invoiced cost |
| `Date` | `ChargePeriodStart` | FOCUS adds separate start/end |
| `ChargeType` == "Usage" | `ChargeCategory` == "Usage" | Unused commitments also appear under Usage in FOCUS |
| `ChargeType` == "Refund" | `ChargeClass` == "Correction" | Refunds are reclassified into individual charge categories |
| `BenefitId` | `CommitmentDiscountId` | Prefer over `ReservationId` to include savings plans |
| `MeterName` | `SkuMeter` | Direct mapping |
| `SubscriptionId` | `SubAccountId` | Direct mapping |
| `BillingPeriodEndDate` + 1 day | `BillingPeriodEnd` | FOCUS uses exclusive end dates |

Full conversion guide: [Convert Cost Management data to FOCUS](https://learn.microsoft.com/cloud-computing/finops/focus/convert)

## Validation

To verify FOCUS data against existing actual cost reports: [Validate FOCUS data](https://learn.microsoft.com/cloud-computing/finops/focus/validate)

## FinOps Toolkit and Analytics Options

Depending on what Ravl/IGM plans to do with the FOCUS data, several Microsoft tools integrate natively.

### FinOps Hubs

A centralized solution for ingesting, governing, and sharing FOCUS cost data across the organization. Hubs normalize data and add enrichments.

[FinOps hubs overview](https://learn.microsoft.com/cloud-computing/finops/toolkit/hubs/finops-hubs-overview)

### Power BI Reports

Pre-built Power BI templates designed for FOCUS data. Cover cost summary, commitment discounts, rate optimization, and more.

[FinOps toolkit Power BI reports](https://learn.microsoft.com/cloud-computing/finops/toolkit/power-bi/reports)

### Microsoft Fabric

FOCUS exports can be used as the input for a Microsoft Fabric workspace, enabling lakehouse-scale analytics over cost data.

[Create a Fabric workspace for FinOps](https://learn.microsoft.com/cloud-computing/finops/fabric/create-fabric-workspace-finops)

### Cost Details API

For on-demand, smaller datasets (not recurring bulk exports), use the Cost Details API programmatically.

[Cost Details API best practices](https://learn.microsoft.com/azure/cost-management-billing/automate/usage-details-best-practices)

## Known Gotchas

These are active limitations and behaviors to be aware of when working with Azure FOCUS data.

1. **Currency difference:** FOCUS uses billing currency for all prices. Native Cost Management uses pricing currency. Prices may appear different if the billing and pricing currencies differ.

2. **Exclusive end dates:** `BillingPeriodEnd` and `ChargePeriodEnd` are exclusive. January's billing period ends on February 1, not January 31. This simplifies filtering but can confuse teams used to inclusive ranges.

3. **BillingAccountId mapping:** For MCA accounts, `BillingAccountId` maps to the billing profile, not the top-level Microsoft billing account. Use `x_BillingAccountId` if you need the top-level account.

4. **InvoiceId availability:** Only populated for MCA accounts after an invoice is generated. Not available for EA.

5. **ServiceName mapping gaps:** The `ServiceName` column is still evolving. Some services may not be correctly mapped yet. AKS charges are identified via a resource group name heuristic that can produce false positives.

6. **Management group scope:** Not supported for FOCUS exports. Use enrollment, billing profile, subscription, or resource group scopes.

7. **Tags in JSON:** FOCUS always provides tags as proper JSON. EA actual/amortized exports sometimes use non-JSON format. This is a positive change but requires updating any parsers that handled the old format.

8. **SkuPriceId for MCA:** Uses the format `{ProductId}_{SkuId}_{MeterType}`. To join FOCUS data with the price sheet, split this value or construct a matching key in the price sheet.

## Discovery Call Checklist

Questions to ask Katie and the Ravl team during the first call.

### Agreement and Scope

- [ ] What Azure agreement type does IGM have? (EA, MCA, or MPA)
- [ ] What scopes are relevant? (enrollment-wide, specific subscriptions, resource groups)
- [ ] Are multiple billing accounts or subscriptions involved?
- [ ] Is IGM using a single cloud (Azure only) or multi-cloud?

### Current State

- [ ] Are they already exporting cost data from Azure? If so, in which format? (actual, amortized, or legacy usage-only)
- [ ] Where does the exported data land today? (Storage account, data lake, third-party tool)
- [ ] Are they using any FinOps tooling already? (Power BI, Fabric, third-party like CloudHealth or Apptio)
- [ ] Do they have existing reports or dashboards that would need to be migrated to FOCUS?

### FOCUS-Specific Questions

- [ ] What is driving the move to FOCUS format specifically? (multi-cloud standardization, FinOps Foundation alignment, simpler reporting)
- [ ] Do they need to run FOCUS alongside existing exports during a transition, or is this a clean start?
- [ ] Are they interested in the FinOps toolkit (hubs, Power BI templates) or building custom analytics?
- [ ] Do they need to join FOCUS data with the Azure price sheet?

### Data Consumers and Use Cases

- [ ] Who will consume the FOCUS data? (finance team, engineering, FinOps practitioners)
- [ ] What are the primary use cases? (chargeback/showback, cost allocation, anomaly detection, rate optimization, budget tracking)
- [ ] Do they need real-time or near-real-time data, or are daily/monthly exports sufficient?
- [ ] Are there compliance or data residency requirements for where the cost data is stored?

### Engagement Logistics

- [ ] Who is the primary technical contact at IGM?
- [ ] What is the timeline or urgency for the FinOps engagement?
- [ ] Are there specific deliverables expected from this PSA engagement?

## Reference Links

| Resource | URL |
|---|---|
| What is FOCUS | <https://learn.microsoft.com/cloud-computing/finops/focus/what-is-focus> |
| FOCUS schema (all versions) | <https://learn.microsoft.com/azure/cost-management-billing/dataset-schema/cost-usage-details-focus> |
| Create and manage exports | <https://learn.microsoft.com/azure/cost-management-billing/costs/tutorial-improved-exports> |
| Convert to FOCUS | <https://learn.microsoft.com/cloud-computing/finops/focus/convert> |
| Validate FOCUS data | <https://learn.microsoft.com/cloud-computing/finops/focus/validate> |
| FinOps hubs | <https://learn.microsoft.com/cloud-computing/finops/toolkit/hubs/finops-hubs-overview> |
| Power BI reports | <https://learn.microsoft.com/cloud-computing/finops/toolkit/power-bi/reports> |
| Fabric for FinOps | <https://learn.microsoft.com/cloud-computing/finops/fabric/create-fabric-workspace-finops> |
| Implementing FinOps guide | <https://learn.microsoft.com/cloud-computing/finops/implementing-finops-guide> |
| FOCUS spec (FinOps Foundation) | <https://focus.finops.org> |
| Learning FOCUS blog series | <https://techcommunity.microsoft.com/blog/finopsblog/learning-focus-introducing-an-open-billing-data-format/4321609> |
| FinOps toolkit open data | <https://learn.microsoft.com/cloud-computing/finops/toolkit/open-data> |
| FOCUS conformance report | <https://learn.microsoft.com/cloud-computing/finops/focus/conformance-full-report> |
| Partner export with SAS key | <https://learn.microsoft.com/azure/cost-management-billing/costs/export-cost-data-storage-account-sas-key> |
