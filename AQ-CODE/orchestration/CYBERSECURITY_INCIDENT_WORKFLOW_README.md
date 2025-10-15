# Cybersecurity Incident Triage Workflow

## Overview

A concurrent fan-out/fan-in workflow that triages cybersecurity incidents through 6 specialized security responders. All agents analyze the incident simultaneously to produce a rapid, actionable triage report with containment priorities and elapsed time tracking.

## Workflow Pattern

**Type:** Concurrent (Fan-out/Fan-in) + Synthesis  
**Agents:** 6 specialized cybersecurity incident responders  
**Processing:** All agents analyze in parallel → Structured triage report  
**Output:** Comprehensive incident assessment with prioritized response actions

## Agent Architecture

```
                    User Input
                        ↓
              Incident Dispatcher
                        ↓
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
   🔍 Threat        🌐 Network       💻 Endpoint
   Intelligence     Forensics        Analyst
        ↓               ↓               ↓
   🧬 Malware        📋 Risk &        🚑 Containment
   Analyst          Compliance       & Remediation
                        ↓
              Incident Aggregator
                        ↓
        Triage Report + Risk Matrix
```

## Agent Specializations

1. **🔍 Threat Intelligence Analyst**
   - Map indicators to known campaigns (MITRE ATT&CK)
   - Attribution hypotheses and threat actor profiling
   - TTPs (Tactics, Techniques, Procedures) identification
   - Intelligence gaps and recommended enrichment

2. **🌐 Network Forensics Specialist**
   - Traffic anomalies and beaconing patterns
   - Lateral movement and pivoting analysis
   - Command-and-control (C2) channel identification
   - Exfiltration paths and recommended network containment

3. **💻 Endpoint / EDR Analyst**
   - Host-based artifacts and forensic evidence
   - Persistence mechanisms (registry, services, scheduled tasks)
   - Privilege escalation attempts
   - Host triage and isolation recommendations

4. **🧬 Malware Analyst**
   - Behavioral and static analysis (when sample available)
   - Encryption, evasion, and anti-analysis techniques
   - Exfiltration capabilities and data targeting
   - Needed forensic artifacts for deeper analysis

5. **📋 Risk & Compliance Officer**
   - Regulatory impact assessment (HIPAA, PCI-DSS, GDPR)
   - Breach notification triggers and deadlines
   - Data classifications affected
   - Compliance risks and reporting requirements

6. **🚑 Containment & Remediation Lead**
   - **0-6 hour actions:** Immediate containment
   - **6-24 hour actions:** Investigation and scoping
   - **1-7 day actions:** Eradication and recovery
   - **Longer-term:** Hardening and resilience improvements

## Use Cases

### Ransomware Incidents
- File server encryption with ransom demand
- Lateral movement across Windows domain
- Backup deletion and shadow copy removal
- Cryptocurrency payment demands

### Data Exfiltration
- Unusual outbound traffic spikes
- TLS connections to unknown domains
- Database queries at unusual times
- Suspected insider threat or compromised credentials

### Phishing & Credential Abuse
- Phishing emails leading to credential reuse
- Abnormal Azure AD/cloud sign-ins from foreign regions
- Mailbox rules or forwarding added
- OAuth token theft and abuse

### Infrastructure Compromise
- Crypto-mining processes in Kubernetes clusters
- Suspicious container images pulled
- PLC/SCADA tampering in industrial control systems
- Unauthorized cloud resource provisioning

### Advanced Persistent Threats (APT)
- PowerShell execution + LSASS memory dumping
- Privilege escalation on domain controllers
- Living-off-the-land (LOL) binaries usage
- Long-term persistence establishment

## Running the Workflow

### Prerequisites
- Azure OpenAI access configured in `.env` file
- Azure CLI authentication: `az login`

### Launch DevUI
```bash
python cybersecurity_incident_triage_devui.py
```

Access at: **http://localhost:8095**

## Output

### Console
- Real-time concurrent analysis status
- Elapsed time from incident dispatch to triage completion

### DevUI
- Interactive visualization
- Live responder analyses
- Scrollable incident report

### Files
Two formats saved to `workflow_outputs/`:
- **TXT:** `cyber_incident_triage_<timestamp>.txt`
- **Markdown:** `cyber_incident_triage_<timestamp>.md`

## Output Structure

```
🛡️ CYBERSECURITY INCIDENT TRIAGE REPORT
════════════════════════════════════════════════════════════════════════════════

(Automated Summary: Review each section for validation.)

🔍 THREAT INTELLIGENCE
────────────────────────────────────────────────────────────────────────────────
Indicators Observed: [IPs, domains, file hashes...]
Likely TTPs: [MITRE ATT&CK techniques - T1486, T1059, T1003...]
Possible Attribution: [Threat actor group, confidence level...]
Intelligence Gaps: [Additional IOCs needed, threat actor capabilities...]

🌐 NETWORK FORENSICS
────────────────────────────────────────────────────────────────────────────────
Suspicious Flows: [Source/destination, protocols, volumes...]
Protocol Anomalies: [JA3 hashes, DNS tunneling, uncommon ports...]
Lateral Movement Hypotheses: [Pivot points, SMB/RDP abuse...]
Recommended Network Containment: [Firewall rules, VLAN isolation...]

💻 ENDPOINT ANALYSIS
────────────────────────────────────────────────────────────────────────────────
Key Host Artifacts: [Processes, file modifications, registry keys...]
Persistence Mechanisms: [Scheduled tasks, services, WMI subscriptions...]
Privilege Escalation Attempts: [Token manipulation, UAC bypass...]
Host Triage Recommendations: [Isolation, memory dumps, disk imaging...]

🧬 MALWARE BEHAVIOR
────────────────────────────────────────────────────────────────────────────────
Behavior Hypotheses: [Encryption, backdoor, data theft...]
Encryption/Exfil Traits: [Crypto algorithms, staging paths...]
Evasion Techniques: [Anti-analysis, obfuscation, sandbox detection...]
Needed Forensic Artifacts: [Sample submission, network PCAPs...]

📋 RISK & COMPLIANCE
────────────────────────────────────────────────────────────────────────────────
Regulatory Considerations: [HIPAA breach? PCI incident? GDPR Article 33?...]
Reporting Deadlines: [72 hours GDPR, state breach laws...]
Data Categories Affected: [PHI, PII, payment card data...]
Compliance Risks: [Fines, audits, regulatory actions...]

🚑 CONTAINMENT & REMEDIATION
────────────────────────────────────────────────────────────────────────────────
0-6h Actions: [Isolate affected hosts, disable accounts, block IPs...]
6-24h Actions: [Forensic collection, scope confirmation, communication plan...]
1-7d Actions: [Eradicate malware, restore from backups, credential reset...]
Longer-Term Hardening: [MFA enforcement, EDR tuning, segmentation...]
Risk Reduction Rationale: [Priority justification, impact minimization...]

════════════════════════════════════════════════════════════════════════════════
✅ Triage complete - validate before execution.
════════════════════════════════════════════════════════════════════════════════
⏱️ Elapsed Time: 18.73 seconds
```

## Key Features

✅ **Rapid triage** - all 6 responders analyze concurrently  
✅ **MITRE ATT&CK mapping** - standardized threat intelligence  
✅ **Time-boxed response** - 0-6h, 6-24h, 1-7d, long-term actions  
✅ **Compliance assessment** - regulatory impact and reporting deadlines  
✅ **Forensic guidance** - artifacts needed for investigation  
✅ **Dual format exports** - TXT and Markdown for incident documentation  
✅ **Elapsed time tracking** - response speed measurement  

## Framework Compatibility

Updated for **Microsoft Agent Framework (new structure)**:
- Custom `Executor` classes for dispatcher and aggregator
- Proper type annotations with `WorkflowContext` and `AgentExecutorResponse`
- `WorkflowBuilder` with fan-out/fan-in edge patterns
- Global timing capture for elapsed metrics
- Compatible with DevUI tracing and visualization

## Incident Response Considerations

### MITRE ATT&CK Framework
- **Initial Access:** T1566 (Phishing), T1190 (Exploit Public-Facing App)
- **Execution:** T1059 (Command and Scripting), T1106 (Native API)
- **Persistence:** T1053 (Scheduled Task), T1547 (Boot/Logon Autostart)
- **Privilege Escalation:** T1055 (Process Injection), T1068 (Exploitation)
- **Defense Evasion:** T1027 (Obfuscation), T1070 (Indicator Removal)
- **Credential Access:** T1003 (LSASS Dumping), T1110 (Brute Force)
- **Lateral Movement:** T1021 (RDP/SMB), T1550 (Token Abuse)
- **Exfiltration:** T1041 (C2 Channel), T1048 (Alternative Protocol)
- **Impact:** T1486 (Data Encrypted for Impact), T1490 (Inhibit Recovery)

### Containment Priorities

**Immediate (0-6h):**
1. **Isolate** affected systems (network segmentation, host quarantine)
2. **Disable** compromised accounts and revoke access tokens
3. **Block** known-bad IPs, domains, file hashes at perimeter
4. **Preserve** evidence (memory dumps, logs, disk images)
5. **Communicate** with stakeholders (executives, legal, PR)

**Short-term (6-24h):**
1. **Scope** the full extent of compromise (log analysis, threat hunting)
2. **Forensics** deep-dive on key systems and artifacts
3. **Attribution** refine threat actor assessment
4. **Communications** external (law enforcement, customers if needed)

**Medium-term (1-7d):**
1. **Eradicate** malware, backdoors, persistence mechanisms
2. **Restore** systems from known-good backups
3. **Reset** credentials (passwords, tokens, certificates)
4. **Patch** vulnerabilities exploited in initial compromise

**Long-term (7d+):**
1. **Harden** systems (MFA, least privilege, network segmentation)
2. **Monitor** for reinfection or related activity
3. **Document** incident timeline, lessons learned, playbook updates
4. **Train** staff on phishing, security awareness

### Regulatory Breach Thresholds

| Regulation | Scope | Notification Deadline | Penalties |
|------------|-------|----------------------|-----------|
| **GDPR** | EU residents' personal data | 72 hours to DPA | Up to €20M or 4% revenue |
| **HIPAA** | Protected Health Information (PHI) | 60 days | Up to $1.5M per violation |
| **PCI-DSS** | Payment card data | Immediate to banks | Fines, card network sanctions |
| **CCPA/CPRA** | California residents' data | Without unreasonable delay | $2,500-$7,500 per violation |
| **State Breach Laws** | Varies by state | 30-90 days typical | Varies, often per-record fines |

### Evidence Preservation

**Critical Forensic Artifacts:**
- **Memory dumps:** Capture volatile data (running processes, network connections)
- **Disk images:** Full forensic copy for offline analysis
- **Event logs:** Windows Event Logs, syslog, application logs
- **Network PCAPs:** Packet captures of suspicious traffic
- **EDR telemetry:** Endpoint detection and response data
- **Cloud logs:** Azure AD, AWS CloudTrail, GCP Audit Logs

**Chain of Custody:**
- Document who collected, when, where, how
- Hash all evidence files (SHA-256) for integrity
- Store in write-protected, access-controlled location
- Maintain audit trail of all evidence handling

## Time-Boxed Response Matrix

| Time Window | Focus | Key Actions | Success Metrics |
|-------------|-------|-------------|-----------------|
| **0-6 hours** | Containment | Isolate, disable, block | Spread stopped |
| **6-24 hours** | Investigation | Scope, forensics, attribution | Extent known |
| **1-7 days** | Eradication | Remove malware, restore systems | Systems clean |
| **7+ days** | Recovery & Hardening | Monitoring, documentation, prevention | Resilience improved |

## Threat Intelligence Sources

### Commercial Feeds
- CrowdStrike Threat Intelligence
- Recorded Future
- Mandiant Threat Intelligence
- Palo Alto Networks Unit 42

### Open Source Intelligence (OSINT)
- MITRE ATT&CK
- AlienVault OTX
- Threat sharing ISACs (FS-ISAC, H-ISAC)
- VirusTotal, Hybrid Analysis

### Government Resources
- CISA alerts and advisories
- FBI IC3 reports
- National Cyber Security Centre (NCSC)

## Tracing Options

Set environment variables to enable tracing:

- **Console:** `ENABLE_CONSOLE_TRACING=true`
- **Application Insights:** `ENABLE_AZURE_AI_TRACING=true`
- **OTLP Endpoint:** `OTLP_ENDPOINT=http://localhost:4317`
- **DevUI Tracing:** `ENABLE_DEVUI_TRACING=true`

## Related Workflows

- **ML Model Productionization:** Sequential gate review for security hardening
- **Biotech IP Landscape:** Debate format with pro/con perspectives
- **Clinical Trial Management:** Concurrent multi-expert analysis pattern

## Port Configuration

Default port: **8095**

To change the port, modify the `port` parameter in the `serve()` call:
```python
serve(entities=[workflow], port=8096, auto_open=True)
```

## Entity ID

Workflow entity ID: **`workflow_cyber_incident`**

Used for API calls and DevUI identification.

## Important Disclaimers

⚠️ **This workflow generates preliminary incident triage for rapid response guidance only.**

- **Not Professional IR Services** - Consult qualified incident response teams
- **Validate All Findings** - AI-generated analysis may miss critical details
- **Legal Considerations** - Involve legal counsel for breach notifications
- **Forensics Integrity** - Follow proper chain of custody procedures
- **Law Enforcement** - Report criminal activity to appropriate authorities
- **Business Continuity** - Balance response actions with operational needs
- **Threat Evolution** - Attackers adapt; continuous monitoring required

## Best Practices

### Input Quality
- **Be Specific:** Include system names, IP addresses, timelines, observed symptoms
- **Provide Context:** Network topology, user population, data classifications
- **List Indicators:** File hashes, domains, IPs, suspicious processes

### Output Usage
- **Cross-Validate:** Correlate findings across multiple responder perspectives
- **Prioritize Actions:** Follow time-boxed response (0-6h first, then 6-24h, etc.)
- **Document Everything:** Maintain incident timeline and decision rationale
- **Iterate:** As new evidence emerges, rerun triage with updated information

### When NOT to Use
- **Active Ransomware Encryption:** Immediately isolate, don't wait for AI analysis
- **Critical Infrastructure:** Follow industry-specific incident response playbooks (e.g., ICS-CERT)
- **Nation-State APT:** Engage specialized threat intelligence and incident response firms
