# Zafin SRE Agent - Technical Challenges & Solutions

**Date:** January 20, 2026  
**Source:** Technical Deep Dive Meeting with Zoya Abou-Jaish (Zafin)  
**Microsoft Team:** Richard Liang, Deepthi Chelupati, Arturo Quiroga

---

## Current Implementation

### Environment Details
- **Use Case:** Production AKS cluster monitoring and incident analysis
- **Data Source:** Log Analytics workspace
- **Permissions:** Reader permissions on subscription
- **Status:** Actively in production

### What's Working
✅ Agent identifies node issues (not ready state, memory pressure)  
✅ Provides health summaries  
✅ Suggests remediation steps (e.g., adjusting memory request limits)  
✅ Instruction tuning improved responsiveness and accuracy  
✅ Targeted queries result in faster, more relevant responses

---

## Technical Challenges

### 1. Context Retention Issues 🔴 **HIGH PRIORITY**

**Problem:**
- Agent loses context between related queries
- Requires re-specification of pod names or details
- Thread-specific context loss (only in threads with extensive interaction)

**Specific Example:**
- When asked to check Redpanda logs, agent searched its own memory and past incident knowledge instead of querying Log Analytics workspace
- Issue only occurred in specific thread with extensive interaction

**Impact:** Medium - Requires user to repeat information, reduces efficiency

**Potential Causes:**
- Possible backend feature causing agent to prioritize incident knowledge over live queries
- Session or memory handling bug in long-running threads
- Context window limitations

**Recommended Solutions:**
1. **Immediate:**
   - Use `/clear` command to reset context when switching topics
   - Break long investigations into separate threads
   - Re-state key context (cluster name, resource IDs) periodically

2. **Short-term:**
   - Deepthi to investigate backend feature enablement
   - Test memory settings in sub-agent configuration
   - Document context retention patterns

3. **Long-term:**
   - Implement context summarization in sub-agent instructions
   - Use session insights to maintain critical context
   - Consider thread splitting automation

**GitHub Issue:** To be created by Zoya

---

### 2. Output Format Consistency 🟡 **MEDIUM PRIORITY**

**Problem:**
- Agent sometimes repeats responses
- Changes output format unexpectedly
- Inconsistent presentation of health data and metrics

**Root Causes:**
- Self-verification process causing repetition
- Instruction ambiguity around format preferences
- No persistent memory of format preferences

**Impact:** Low-Medium - Requires manual reformatting, user confusion

**Recommended Solutions:**
1. **Immediate:**
   - Specify preferred output format explicitly in sub-agent instructions
   - Use `/remember` command to teach format preferences
   - Example: `/remember Always present cluster health in table format with columns: Node, Status, CPU%, Memory%, Ready State`

2. **Short-term:**
   - Add format examples to session insights
   - Enable memory in sub-agent to persist preferences
   - Create output format templates in knowledge base

3. **Long-term:**
   - Develop standard output schemas for common queries
   - Implement format validation in sub-agent logic

**Sample Instruction Enhancement:**
```yaml
instructions: |
  When presenting cluster health information:
  1. Use markdown tables with columns: Resource, Status, Issue, Recommendation
  2. Always highlight critical issues in bold
  3. Include timestamp of data retrieval
  4. Provide summary count at the end
  5. Do not repeat information unless explicitly asked
```

---

### 3. Resource Identification - Cosmos DB 🟡 **MEDIUM PRIORITY**

**Problem:**
- Agent fails to find Cosmos DB resources without exact resource ID
- Sometimes returns only PostgreSQL flexible servers when searching databases
- Knowledge graph may not include all Cosmos DB types

**Examples:**
- Generic query: "Show me all databases" → Returns PostgreSQL only
- Must specify: "Search all managed database types including Cosmos DB"

**Impact:** Medium - Incomplete resource discovery, missed monitoring coverage

**Potential Causes:**
- Knowledge graph limitations
- Resource type filtering in queries
- Azure Resource Graph query scope

**Recommended Solutions:**
1. **Immediate Workaround:**
   - Provide explicit resource IDs for Cosmos DB resources
   - Update sub-agent instructions to expand search to all database types
   - Example instruction: "When searching for databases, query all Azure database types: SQL Database, PostgreSQL, MySQL, Cosmos DB (all APIs), and managed instances"

2. **Investigation Needed:**
   - Document which Cosmos DB API types are missing (SQL, MongoDB, Cassandra, Gremlin, Table)
   - Test with explicit resource type queries
   - Verify subscription permissions include Cosmos DB resources

3. **GitHub Issue:**
   - Document exact queries that fail
   - Provide resource IDs that should be found but aren't
   - List Cosmos DB SKUs/types in the subscription

**Sample Test Query:**
```kusto
Resources
| where type in ("Microsoft.DocumentDB/databaseAccounts", 
                 "Microsoft.DBforPostgreSQL/flexibleServers",
                 "Microsoft.DBforMySQL/flexibleServers",
                 "Microsoft.Sql/servers")
| project name, type, location, resourceGroup
```

**GitHub Issue:** To be created by Zoya

---

### 4. Data Completeness & Accuracy 🟡 **MEDIUM PRIORITY**

**Problem:**
- Pod memory utilization queries sometimes miss pods exceeding limits
- Agent doesn't always highlight node readiness and memory issues accurately
- May be using averages instead of peak analysis

**Specific Issues:**
- Pods terminated due to OOM (Out of Memory) not always shown
- Requires more specific prompts to retrieve accurate information
- Data lag in Log Analytics causes outdated status information

**Impact:** Medium - Potential to miss critical incidents

**Root Causes:**
- KQL query logic (averaging vs. max/peak)
- Time range selection in queries
- Incomplete log ingestion or delays

**Recommended Solutions:**
1. **Query Optimization:**
   - Use `max()` or `percentile(95)` instead of `avg()`
   - Expand time window for terminated pods search
   - Add explicit filters for pod states (Failed, OOMKilled, etc.)

2. **Instruction Tuning:**
```yaml
instructions: |
  For memory analysis:
  1. Query PEAK memory usage, not averages
  2. Look for pods in Failed, OOMKilled, or Evicted states
  3. Check both current status AND termination history
  4. Time range: Last 1 hour for current, last 24 hours for terminated
  5. Highlight any node with memory pressure events
```

3. **Sample KQL Queries:**
```kusto
// Peak memory usage
KubePodInventory
| where ClusterName == "your-cluster"
| where TimeGenerated > ago(1h)
| summarize PeakMemory = max(MemoryRequestMBytes) by Name, Namespace
| where PeakMemory > MemoryLimitMBytes * 0.9

// Terminated pods
KubePodInventory
| where TimeGenerated > ago(24h)
| where PodStatus in ("Failed", "Unknown")
| where ContainerStatusReason has_any ("OOMKilled", "Error")
| project TimeGenerated, Name, Namespace, PodStatus, ContainerStatusReason
```

4. **Data Freshness:**
   - Add data timestamp to agent responses
   - Alert user if data is >5 minutes old
   - Implement refresh command

---

### 5. Missing Capabilities 🟢 **LOW PRIORITY (FEATURE REQUESTS)**

**Problem:**
- No file generation capability for reports/exports
- No view trace feature for debugging agent queries

**Impact:** Low - Workarounds available

**File Generation:**
- **Need:** Export incident reports, runbooks, configurations
- **Workaround:** Copy/paste from agent responses
- **GitHub Issue:** To be created by Zoya

**View Trace:**
- **Need:** See which KQL queries are executed
- **Purpose:** Debug inconsistent outputs, optimize queries
- **Status:** Feature request already filed (Deepthi tracking)

---

### 6. Permissions & Access Control 🟢 **INFORMATIONAL**

**Current State:**
- Only SRE Admins can grant additional permissions
- SRE Readers and Users have limited access
- Agent has Reader permissions on subscription

**Issues Encountered:**
- Cannot access certain resource health data (e.g., Application Gateway backend health)
- Need additional permissions for write operations (if remediation enabled)

**Recommended Approach:**
1. **Current State Assessment:**
   - Document what data cannot be accessed
   - Map to specific Azure RBAC permissions needed
   - Evaluate security implications

2. **Permission Request Process:**
   - Work with Zafin security team
   - Follow principle of least privilege
   - Use managed identity best practices

3. **Access Levels:**
   - **Reader (current):** Query logs, view resource properties
   - **Monitoring Contributor:** Access metrics, diagnostics settings
   - **Contributor:** Execute remediation actions (if needed)

---

## Optimization Opportunities

### 1. Knowledge Base Integration ⭐ **RECOMMENDED**

**Opportunity:**
Add troubleshooting runbooks and knowledge files to agent's knowledge base

**Benefits:**
- Agent references team-specific procedures
- Consistent application of organizational best practices
- Faster incident resolution with documented patterns

**Implementation:**
1. **Identify Key Documents:**
   - AKS troubleshooting runbooks
   - Common incident resolution procedures
   - Memory optimization guidelines
   - Performance tuning best practices

2. **Format for Knowledge Base:**
   - Convert to markdown or PDF
   - Structure with clear headings
   - Include examples and KQL queries
   - Tag by incident type

3. **Sub-Agent Configuration:**
```yaml
knowledge_sources:
  - type: files
    files:
      - "aks-memory-troubleshooting.md"
      - "pod-crash-loop-runbook.md"
      - "node-not-ready-procedure.md"
  - type: memory
    enabled: true
    
instructions: |
  Always check knowledge base for established procedures before suggesting remediation.
  Reference specific runbook sections when providing recommendations.
```

4. **Example Knowledge Base Document:**
```markdown
# AKS Memory Troubleshooting Runbook

## Symptoms
- Pods in OOMKilled state
- Nodes showing MemoryPressure
- Application performance degradation

## Diagnostic Steps
1. Check pod memory limits vs. usage
   ```kusto
   KubePodInventory | where ...
   ```
2. Review node allocatable memory
3. Analyze historical memory trends

## Common Resolutions
- Increase memory limits
- Add node pool capacity
- Implement pod autoscaling
- Review memory leaks in application

## Escalation Criteria
- Issue persists >30 minutes after remediation
- Multiple nodes affected simultaneously
```

---

### 2. Sub-Agent Memory Configuration ⭐ **RECOMMENDED**

**Current State:** Memory may not be enabled in sub-agent

**Recommendation:** Enable memory to improve consistency

**Configuration:**
```yaml
sub_agent:
  name: "AKS-Incident-Analyzer"
  memory:
    enabled: true
    retention_policy: session  # or: permanent, time-based
  learning:
    enabled: true
    feedback_incorporation: true
```

**Benefits:**
- Remember user preferences (output format, detail level)
- Retain context about cluster-specific configurations
- Apply learned patterns across sessions
- Reduce repeated instructions

---

### 3. Instruction Tuning Best Practices ⭐ **RECOMMENDED**

**Current Success:**
Zafin's instruction tuning resulted in improved agent performance

**Recommended Approach:**

1. **Start with Clear Objectives:**
```yaml
primary_objectives:
  - Identify AKS cluster health issues within 30 seconds
  - Provide actionable remediation steps aligned with team procedures
  - Present data in consistent, parseable format
```

2. **Specify Query Patterns:**
```yaml
query_strategy:
  - Always query Log Analytics workspace first
  - Use time range: last 1 hour for current state, 24 hours for history
  - Prioritize PEAK metrics over averages
  - Include resource context (cluster name, subscription)
```

3. **Define Output Standards:**
```yaml
output_requirements:
  format: "Markdown tables with severity indicators"
  structure: "Issue → Evidence → Recommendation → Escalation Criteria"
  verbosity: "Concise for routine issues, detailed for complex scenarios"
```

4. **Handle Edge Cases:**
```yaml
edge_case_handling:
  - If no data found, suggest time range expansion
  - If multiple issues, prioritize by severity
  - If context unclear, ask clarifying question before querying
```

5. **Iterative Refinement:**
   - Test with real incidents
   - Document what works and what doesn't
   - Adjust based on user feedback
   - Version control instructions

---

## Immediate Action Plan

### Week 1 (Current)
- [x] Document technical challenges (this document)
- [ ] Zoya creates 3 GitHub issues
- [ ] Arturo reviews engagement context
- [ ] Team alignment meeting

### Week 2
- [ ] Deepthi investigates context loss behavior
- [ ] Implement output format improvements (instructions + `/remember`)
- [ ] Document Cosmos DB identification patterns
- [ ] Test knowledge base integration with sample runbook

### Week 3-4
- [ ] Add troubleshooting runbooks to knowledge base
- [ ] Enable sub-agent memory
- [ ] Refine instructions based on testing
- [ ] Address permission gaps (if needed)

### Week 5-6
- [ ] Optimize KQL queries for data completeness
- [ ] Implement context retention improvements
- [ ] Test file generation workarounds
- [ ] Document best practices learned

---

## Success Metrics

### Response Quality
- ✅ **Target:** 95% of queries return complete, accurate data
- 📊 **Current:** ~80% (estimated based on meeting discussion)
- 🎯 **Gap:** Missing pods, inconsistent formatting

### Response Time
- ✅ **Target:** <30 seconds for cluster health summary
- 📊 **Current:** Achieved after instruction tuning
- 🎯 **Maintained**

### Context Retention
- ✅ **Target:** 90% context retention across related queries
- 📊 **Current:** ~60% (requires re-specification frequently)
- 🎯 **Gap:** Thread-specific context loss

### Remediation Accuracy
- ✅ **Target:** Recommendations align with team procedures 100%
- 📊 **Current:** Successful when knowledge base used
- 🎯 **Opportunity:** Add more runbooks

---

## Resources & References

### Internal Documentation
- [SRE-AGENT-REFERENCE.md](./SRE-AGENT-REFERENCE.md) - General SRE Agent guide
- [Microsoft SRE Agent Repo](https://github.com/microsoft/sre-agent)
- Workspace observability samples: `../AQ-CODE/observability/`

### Relevant Microsoft Docs
- [Azure Monitor KQL Reference](https://learn.microsoft.com/azure/azure-monitor/logs/kql-quick-reference)
- [AKS Monitoring Best Practices](https://learn.microsoft.com/azure/aks/monitor-aks)
- [Azure SRE Agent Documentation](https://learn.microsoft.com/azure/sre-agent/)

### KQL Query Library for AKS
```kusto
// Cluster health summary
KubeNodeInventory
| where TimeGenerated > ago(5m)
| summarize 
    TotalNodes = count(),
    ReadyNodes = countif(Status == "Ready"),
    NotReadyNodes = countif(Status != "Ready")
| extend HealthPercentage = ReadyNodes * 100 / TotalNodes

// Memory pressure detection
KubeEvents
| where TimeGenerated > ago(1h)
| where Reason == "MemoryPressure"
| summarize Count = count() by Computer
| order by Count desc

// Pod terminations
ContainerInventory
| where TimeGenerated > ago(24h)
| where ContainerState == "Failed"
| project TimeGenerated, Name, ContainerStatus, ExitCode
| order by TimeGenerated desc
```

---

## Contact for Technical Questions

- **Zafin Lead:** Zoya Abou-Jaish
- **MS AI PSA:** Arturo Quiroga
- **MS Apps PSA:** Tommy Falgout
- **MS Strategy:** Richard Liang
- **MS Support:** Deepthi Chelupati

---

## Document Version

| Date | Author | Changes |
|------|--------|---------|
| 2026-01-20 | Arturo Quiroga | Initial creation from meeting notes |
