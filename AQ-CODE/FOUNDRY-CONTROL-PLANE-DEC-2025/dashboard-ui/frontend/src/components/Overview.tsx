import {
  Card,
  Title,
  DonutChart,
  BarChart,
  Grid,
  Flex,
  Text,
  BadgeDelta,
  Legend,
} from "@tremor/react";
import type { FleetSummary } from "../types";
import KpiCard from "./KpiCard";

interface Props {
  data: FleetSummary;
}

export default function Overview({ data }: Props) {
  const totalAlerts =
    data.critical_alerts +
    data.high_alerts +
    data.medium_alerts +
    data.low_alerts;

  const healthDist = [
    { name: "Healthy", value: data.healthy_agents },
    { name: "Warning", value: data.warning_agents },
    { name: "Critical", value: data.critical_agents },
  ];

  const agentRuns = [...data.agents]
    .sort((a, b) => b.total_runs - a.total_runs)
    .slice(0, 10)
    .map((a) => ({
      name: a.agent_name,
      Successful: a.successful_runs,
      Failed: a.failed_runs,
    }));

  const alertSeverity = [
    { name: "Critical", value: data.critical_alerts },
    { name: "High", value: data.high_alerts },
    { name: "Medium", value: data.medium_alerts },
    { name: "Low", value: data.low_alerts },
  ].filter((d) => d.value > 0);

  return (
    <div className="space-y-6">
      {/* KPI row */}
      <Grid numItemsSm={2} numItemsLg={3} numItems={6} className="gap-4">
        <KpiCard
          title="Fleet Health Score"
          value={`${data.fleet_health_score.toFixed(1)}%`}
          subtitle={`${data.active_agents} active agents`}
          icon="🎯"
          color="blue"
        />
        <KpiCard
          title="Total Agents"
          value={String(data.total_agents)}
          subtitle={`✅${data.healthy_agents}   ⚠️${data.warning_agents}   🔴${data.critical_agents}`}
          icon="🤖"
          color="emerald"
        />
        <KpiCard
          title="Success Rate"
          value={`${(data.avg_success_rate * 100).toFixed(1)}%`}
          subtitle={`${data.total_runs_24h.toLocaleString()} runs (24h)`}
          icon="📈"
          color="cyan"
        />
        <KpiCard
          title="Cost (7d)"
          value={`$${data.total_cost_7d.toFixed(2)}`}
          subtitle={`$${data.total_cost_24h.toFixed(2)}/day avg`}
          icon="💵"
          delta={
            data.cost_trend_pct
              ? `${data.cost_trend_pct > 0 ? "+" : ""}${data.cost_trend_pct.toFixed(1)}%`
              : undefined
          }
          deltaType={data.cost_trend_pct < 0 ? "moderateDecrease" : "moderateIncrease"}
          color="amber"
        />
        <KpiCard
          title="Active Alerts"
          value={String(totalAlerts)}
          subtitle={`🔴${data.critical_alerts}  🟠${data.high_alerts}  🟡${data.medium_alerts}`}
          icon="🚨"
          color={data.critical_alerts > 0 ? "red" : data.high_alerts > 0 ? "amber" : "emerald"}
        />
        <KpiCard
          title="Compliance"
          value={`${data.compliant_agents}/${data.total_agents}`}
          subtitle={`${data.total_policy_violations} violations`}
          icon="🛡️"
          color={data.non_compliant_agents === 0 ? "emerald" : "amber"}
        />
      </Grid>

      {/* Charts row */}
      <Grid numItemsSm={1} numItemsLg={3} className="gap-6">
        <Card>
          <Title>🏥 Health Distribution</Title>
          <DonutChart
            className="mt-4 h-52"
            data={healthDist}
            category="value"
            index="name"
            colors={["emerald", "amber", "red"]}
            showLabel
            label={`${data.fleet_health_score.toFixed(0)}%`}
          />
          <Legend
            className="mt-3 justify-center"
            categories={["Healthy", "Warning", "Critical"]}
            colors={["emerald", "amber", "red"]}
          />
        </Card>

        <Card>
          <Title>📊 Runs by Agent (24h)</Title>
          <BarChart
            className="mt-4 h-52"
            data={agentRuns}
            index="name"
            categories={["Successful", "Failed"]}
            colors={["emerald", "red"]}
            stack
            showLegend
          />
        </Card>

        <Card>
          <Title>🚨 Alerts by Severity</Title>
          {alertSeverity.length > 0 ? (
            <DonutChart
              className="mt-4 h-52"
              data={alertSeverity}
              category="value"
              index="name"
              colors={["red", "orange", "amber", "cyan"]}
            />
          ) : (
            <Flex justifyContent="center" alignItems="center" className="h-52">
              <Text>🎉 No active alerts</Text>
            </Flex>
          )}
        </Card>
      </Grid>

      {/* Quick Actions + Health Factors */}
      <Grid numItemsSm={1} numItemsLg={2} className="gap-6">
        <Card>
          <Title>⚡ Quick Actions</Title>
          <div className="mt-4 flex flex-wrap gap-2">
            {[
              { label: "Foundry Operate Tab", href: "https://ai.azure.com", icon: "🤖" },
              { label: "Application Insights", href: "https://portal.azure.com/#blade/HubsExtension/BrowseResource/resourceType/microsoft.insights%2Fcomponents", icon: "📈" },
              { label: "Grafana Agent Dashboard", href: "https://aka.ms/amg/dash/af-agent", icon: "📊" },
              { label: "Grafana Workflow Dashboard", href: "https://aka.ms/amg/dash/af-workflow", icon: "📊" },
              { label: "Defender for Cloud", href: "https://portal.azure.com/#blade/Microsoft_Azure_Security/SecurityMenuBlade/overview", icon: "🛡️" },
            ].map((link) => (
              <a
                key={link.label}
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
                className="inline-flex items-center gap-1.5 rounded-lg border border-tremor-border px-3 py-1.5 text-sm text-tremor-content-emphasis hover:bg-tremor-background-muted transition"
              >
                <span>{link.icon}</span>
                {link.label}
              </a>
            ))}
          </div>
        </Card>

        <Card>
          <Title>📋 Health Score Factors</Title>
          <ul className="mt-4 space-y-2 text-sm text-tremor-content">
            <li>✅ <strong>Error Rate &lt; 5%</strong> — Low failure rate</li>
            <li>✅ <strong>Latency &lt; 2s</strong> — Fast response times</li>
            <li>✅ <strong>No violations</strong> — Compliance maintained</li>
            <li>✅ <strong>Active in 24h</strong> — Recent activity</li>
            <li>✅ <strong>Has instructions</strong> — System prompt defined</li>
          </ul>
          <Text className="mt-4 text-xs text-tremor-content-subtle">
            <strong>New in Feb 2026:</strong> Continuous Evaluation, AI Red
            Teaming Agent, Grafana dashboards, Agent lifecycle
            (start/stop/block), Custom agent registration
          </Text>
        </Card>
      </Grid>
    </div>
  );
}
