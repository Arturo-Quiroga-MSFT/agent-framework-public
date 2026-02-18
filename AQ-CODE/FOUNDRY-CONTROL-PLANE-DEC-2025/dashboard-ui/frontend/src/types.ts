/* Fleet Health Dashboard — shared types */

export interface AgentMetrics {
  agent_id: string;
  agent_name: string;
  agent_version: string;
  model: string;
  status: "healthy" | "warning" | "critical" | "unknown";
  health_score: number;
  tools: string[];
  total_runs: number;
  successful_runs: number;
  failed_runs: number;
  error_rate: number;
  avg_latency_ms: number;
  p95_latency_ms: number;
  total_tokens: number;
  prompt_tokens: number;
  completion_tokens: number;
  estimated_cost_usd: number;
  compliance_status: string;
  policy_violations: number;
}

export interface Alert {
  timestamp: string;
  message: string;
  severity: "critical" | "high" | "medium" | "low";
  agent_name: string;
  source: string;
}

export interface ComplianceIssue {
  agent_name: string;
  rule: string;
  severity: string;
  message: string;
  recommendation: string;
}

export interface FleetSummary {
  total_agents: number;
  active_agents: number;
  healthy_agents: number;
  warning_agents: number;
  critical_agents: number;
  fleet_health_score: number;
  avg_success_rate: number;
  total_runs_24h: number;
  total_errors_24h: number;
  total_cost_24h: number;
  total_cost_7d: number;
  total_tokens_24h: number;
  cost_trend_pct: number;
  compliant_agents: number;
  non_compliant_agents: number;
  total_policy_violations: number;
  critical_alerts: number;
  high_alerts: number;
  medium_alerts: number;
  low_alerts: number;
  agents: AgentMetrics[];
  alerts: Alert[];
  compliance_violations: ComplianceIssue[];
  compliance_warnings: ComplianceIssue[];
  generated_at: string;
  data_source: string;
}
