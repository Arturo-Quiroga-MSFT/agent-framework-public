

### Recommended research/prep order

**1. Understand Ravl's agreement type first** (critical prerequisite)
FOCUS export support varies by agreement type (EA, MCA, MPA). Before the discovery call, you need to know whether IGM (the end customer) is on an Enterprise Agreement or Microsoft Customer Agreement, because that determines:
- Which scopes are supported for FOCUS exports
- Whether `InvoiceId` is available (MCA only)
- How `BillingAccountId` maps (different for EA vs MCA)
- Management group scope is *not* supported for FOCUS exports

**2. FOCUS export setup via Azure Cost Management**
The most likely ask: how to configure Cost Management exports in FOCUS format. Key docs:
- [Tutorial: Create and manage exports](https://learn.microsoft.com/azure/cost-management-billing/costs/tutorial-improved-exports) — the step-by-step for enabling "Cost and usage details (FOCUS)" exports
- FOCUS combines actual and amortized costs into a single dataset (~30% smaller than running both separately)

**3. FOCUS schema and column mapping**
If they already have non-FOCUS exports and are migrating, the [column mapping from actual/amortized to FOCUS](https://learn.microsoft.com/cloud-computing/finops/focus/convert) and the [validation guide](https://learn.microsoft.com/cloud-computing/finops/focus/validate) are essential. FOCUS v1.2-preview has 105 columns (53 FOCUS-standard + 52 `x_` extensions).

**4. FinOps toolkit integration** (likely their end goal)
If Ravl's FinOps engagement with IGM involves analytics/reporting, they'll likely need:
- [FinOps hubs](https://learn.microsoft.com/cloud-computing/finops/toolkit/hubs/finops-hubs-overview) — central storage + governance for FOCUS data
- [FinOps toolkit Power BI reports](https://learn.microsoft.com/cloud-computing/finops/toolkit/power-bi/reports) — pre-built dashboards
- [Microsoft Fabric workspace for FinOps](https://learn.microsoft.com/cloud-computing/finops/fabric/create-fabric-workspace-finops) — if they want to ingest FOCUS exports into Fabric

**5. Gotchas to prepare for** (common partner questions)
- FOCUS uses **billing currency** for all prices, while native Cost Management uses pricing currency — prices may appear different
- `BillingPeriodEnd` and `ChargePeriodEnd` are **exclusive** dates (Feb 1 instead of Jan 31)
- `ServiceName` mapping is still evolving and may miss some services
- AKS charge attribution has known false positives based on resource group name matching
- Tags are consistently JSON-formatted in FOCUS (unlike raw EA data)

### Suggested first action

Prepare a brief "FOCUS primer" document for the initial discovery call that covers the export setup, schema overview, and a checklist of questions to ask Katie (agreement type, current export setup, what they're building with the data, target analytics platform). That positions you well regardless of where the conversation goes.

