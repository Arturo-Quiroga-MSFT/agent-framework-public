import {
  Card,
  Title,
  BarChart,
  Grid,
  Text,
  Callout,
} from "@tremor/react";
import type { FleetSummary } from "../types";
import KpiCard from "./KpiCard";

interface Props {
  data: FleetSummary;
}

export default function CostAnalysis({ data }: Props) {
  const costByAgent = [...data.agents]
    .sort((a, b) => b.estimated_cost_usd - a.estimated_cost_usd)
    .slice(0, 10)
    .map((a) => ({ name: a.agent_name, Cost: Number(a.estimated_cost_usd.toFixed(4)) }));

  const tokensByAgent = [...data.agents]
    .sort((a, b) => b.total_tokens - a.total_tokens)
    .slice(0, 10)
    .map((a) => ({ name: a.agent_name, Tokens: a.total_tokens }));

  return (
    <div className="space-y-6">
      {/* KPIs */}
      <Grid numItemsSm={2} numItemsLg={4} className="gap-4">
        <KpiCard
          title="Total Cost (7d)"
          value={`$${data.total_cost_7d.toFixed(2)}`}
          subtitle="All agents combined"
          icon="💵"
          color="blue"
        />
        <KpiCard
          title="Daily Average"
          value={`$${data.total_cost_24h.toFixed(2)}`}
          subtitle="Cost per day"
          icon="📅"
          color="cyan"
        />
        <KpiCard
          title="Total Tokens (24h)"
          value={data.total_tokens_24h.toLocaleString()}
          subtitle="Tokens consumed"
          icon="🔢"
          color="gray"
        />
        <KpiCard
          title="Cost Trend"
          value={`${data.cost_trend_pct > 0 ? "+" : ""}${data.cost_trend_pct.toFixed(1)}%`}
          subtitle="vs previous period"
          icon="📈"
          color={data.cost_trend_pct < 0 ? "emerald" : "red"}
        />
      </Grid>

      {/* Charts */}
      <Grid numItemsSm={1} numItemsLg={2} className="gap-6">
        <Card>
          <Title>💰 Cost by Agent (Top 10)</Title>
          <BarChart
            className="mt-4 h-64"
            data={costByAgent}
            index="name"
            categories={["Cost"]}
            colors={["blue"]}
            valueFormatter={(v) => `$${v.toFixed(4)}`}
          />
        </Card>

        <Card>
          <Title>📊 Token Usage by Agent (Top 10)</Title>
          <BarChart
            className="mt-4 h-64"
            data={tokensByAgent}
            index="name"
            categories={["Tokens"]}
            colors={["cyan"]}
            valueFormatter={(v) => v.toLocaleString()}
          />
        </Card>
      </Grid>

      {/* Tips */}
      <Card>
        <Title>💡 Cost Optimization Tips</Title>
        <ul className="mt-3 space-y-2 text-sm text-tremor-content">
          <li>• Switch to smaller models (<code>gpt-4o-mini</code>) for simple tasks</li>
          <li>• Implement response caching for repeated queries</li>
          <li>• Set maximum token limits per request</li>
          <li>• Use batch processing for bulk operations</li>
          <li>• Monitor and alert on unusual cost spikes</li>
        </ul>
      </Card>
    </div>
  );
}
