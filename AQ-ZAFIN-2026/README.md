# Zafin SRE Agent Engagement - 2026

**Engagement Type:** PSA Support  
**Start Date:** January 20, 2026  
**PSA Lead:** Arturo Quiroga  
**Status:** Active

---

## Engagement Overview

Zafin is adopting **Azure SRE Agent** and requires specialized support with:
- Observability and monitoring best practices
- Agent architecture and design patterns
- Integration with existing systems
- Production deployment guidance

---

## Key Documents

### Primary References
- **[SRE-AGENT-REFERENCE.md](./SRE-AGENT-REFERENCE.md)** - Comprehensive guide to SRE Agent capabilities, architecture patterns, and Microsoft's reference implementation
- **[ZAFIN-TECHNICAL-CHALLENGES.md](./ZAFIN-TECHNICAL-CHALLENGES.md)** - ⭐ Current technical challenges, solutions, and optimization opportunities from Jan 20 meeting

### Related Workspace Resources
- **Observability Patterns:** `../AQ-CODE/observability/`
- **LLMOps Best Practices:** `../LLMOPS/`
- **Agent Framework Samples:** `../maf-upstream/python/samples/`
- **Database Assistant Reference:** `../DBMS-ASSISTANT/`

---

## External References

### Microsoft Resources
- **GitHub Repository:** https://github.com/microsoft/sre-agent
- **Azure Documentation:** https://learn.microsoft.com/en-us/azure/sre-agent/overview
- **Deployment Samples:** https://github.com/microsoft/sre-agent/tree/main/samples

### Key Samples to Review
1. **Proactive Reliability Demo** - Complete end-to-end scenario with baseline learning, autonomous remediation, and reporting
2. **Bicep Deployment** - Infrastructure as Code templates for production deployment
3. **Incident Automation** - Integration patterns for incident management platforms

---

## Engagement Contacts

### Microsoft Team
- **PSA/Architect:** Arturo Quiroga (joining as new architect, replacing Eric Leonard)
- **Apps PSA:** Tommy Falgout (Partner Solutions Architect)
- **Partner Technology Strategist:** Richard Liang
- **Technical Support:** Deepthi Chelupati

### Zafin Team
- **Technical Lead:** Zoya Abou-Jaish
- **Project Manager:** TBD
- **Key Stakeholders:** TBD

---

## Meeting Notes

### January 20, 2026 - Zafin Technical Deep Dive
**Attendees:** Richard Liang (MS), Deepthi Chelupati (MS), Zoya Abou-Jaish (Zafin)

**Current State:**
- Zafin is actively using SRE Agent for AKS cluster monitoring and incident analysis
- Successfully tuned agent instructions for improved responsiveness
- Agent queries Log Analytics workspace with reader permissions on subscription

**Key Achievements:**
- Agent successfully identifies node issues (e.g., not ready state due to memory pressure)
- Provides health summaries and remediation suggestions
- Instruction tuning resulted in faster, more relevant responses

**Technical Challenges Identified:**
1. **Context Retention Issues**
   - Agent loses context between related queries
   - Requires re-specification of details (pod names, etc.)
   - Redpanda log query issue: agent searched its own memory instead of Log Analytics

2. **Output Format Consistency**
   - Agent sometimes repeats responses or changes formats unexpectedly
   - Need to enforce preferred formats via instructions and `/remember` command

3. **Resource Identification**
   - Cosmos DB resources not reliably identified without explicit resource IDs
   - Knowledge graph may not include all Cosmos DB types

4. **Data Completeness**
   - Pod memory utilization queries sometimes miss pods exceeding limits
   - Node readiness issues not always highlighted (may be averaging vs. peak analysis)
   - Data lag in Log Analytics can cause outdated status information

5. **Missing Capabilities**
   - Need file generation tool
   - Need view trace capability for query debugging

**Action Items:**
- Zoya to create GitHub issues for: context loss, Cosmos DB identification, file generator
- Deepthi to investigate incident knowledge search behavior
- Add troubleshooting runbooks to agent knowledge base
- Enable memory in sub-agent for consistent applicat (Brian Moore coordination)
- Christian Thilmany mentioned prior Zafin work experience
- Richard Liang conducted technical deep dive meeting same day
- Zafin is already in production with SRE Agent for AKS monitoring
- Primary use case: Production AKS cluster incident analysis and remediation
- Focus areas: Instruction tuning, context retention, observability integration, knowledge base enhancement

## Deliverables

### Phase 1: Discovery & Planning
- [ ] Architecture review and assessment
- [ ] Integration point identification
- [ ] Success criteria definition
- [ ] Implementation roadmap

### Phase 2: Implementation Support
- [ ] Observability setup and configuration
- [ ] Agent development best practices
- [ ] Integration pattern implementation
- [ ] Code reviews and optimization

### Phase 3: Production Readiness
- [ ] Deployment automation
- [ ] Monitoring and alerting setup
- [ ] Runbook documentation
- [ ] Knowledge transfer

---

## Working Files

_Add engagement-specific working files here as they are created_

- Design documents
- Architecture diagrams
- Code samples
- Configuration templates
- Test plans

---

## Notes

- Initial request came via Teams on January 20, 2026
- Brian Moore (EPS) coordinated the engagement
- Christian Thilmany mentioned prior Zafin work experience
- Focus areas: Observability, agent best practices, SRE adoption

---

## Quick Links

- [Teams Channel](#) - TBD
- [Zafin Project Repository](#) - TBD
- [Engagement Tracking](#) - TBD
