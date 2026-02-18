import {
  Card,
  Title,
  Table,
  TableHead,
  TableHeaderCell,
  TableBody,
  TableRow,
  TableCell,
  Badge,
  DonutChart,
  Grid,
  Text,
} from "@tremor/react";
import type { FleetSummary, Alert } from "../types";
import KpiCard from "./KpiCard";

interface Props {
  data: FleetSummary;
}

const SEVERITY_COLOR: Record<string, "red" | "orange" | "amber" | "cyan" | "gray"> = {
  critical: "red",
  high: "orange",
  medium: "amber",
  low: "cyan",
};

export default function AlertsPanel({ data }: Props) {
  const chartData = [
    { name: "Critical", value: data.critical_alerts },
    { name: "High", value: data.high_alerts },
    { name: "Medium", value: data.medium_alerts },
    { name: "Low", value: data.low_alerts },
  ].filter((d) => d.value > 0);

  return (
    <div className="space-y-6">
      {/* Summary KPIs */}
      <Grid numItemsSm={2} numItemsLg={4} className="gap-4">
        <KpiCard title="Critical" value={String(data.critical_alerts)} subtitle="Immediate action" icon="🔴" color="red" />
        <KpiCard title="High" value={String(data.high_alerts)} subtitle="Review within 4h" icon="🟠" color="orange" />
        <KpiCard title="Medium" value={String(data.medium_alerts)} subtitle="Monitor closely" icon="🟡" color="amber" />
        <KpiCard title="Low" value={String(data.low_alerts)} subtitle="Informational" icon="🔵" color="cyan" />
      </Grid>

      <Grid numItemsSm={1} numItemsLg={2} className="gap-6">
        {/* Severity chart */}
        <Card>
          <Title>📊 Alert Distribution</Title>
          {chartData.length > 0 ? (
            <DonutChart
              className="mt-4 h-52"
              data={chartData}
              category="value"
              index="name"
              colors={["red", "orange", "amber", "cyan"]}
            />
          ) : (
            <Text className="mt-8 text-center">🎉 No active alerts</Text>
          )}
        </Card>

        {/* Alert table */}
        <Card>
          <Title>📋 Recent Alerts ({data.alerts.length})</Title>
          {data.alerts.length === 0 ? (
            <Text className="mt-8 text-center text-emerald-600">
              🎉 No active alerts in the last 24 hours!
            </Text>
          ) : (
            <Table className="mt-4">
              <TableHead>
                <TableRow>
                  <TableHeaderCell>Severity</TableHeaderCell>
                  <TableHeaderCell>Message</TableHeaderCell>
                  <TableHeaderCell>Agent</TableHeaderCell>
                  <TableHeaderCell>Source</TableHeaderCell>
                </TableRow>
              </TableHead>
              <TableBody>
                {data.alerts.slice(0, 20).map((alert: Alert, i: number) => (
                  <TableRow key={i}>
                    <TableCell>
                      <Badge color={SEVERITY_COLOR[alert.severity] ?? "gray"}>
                        {alert.severity}
                      </Badge>
                    </TableCell>
                    <TableCell className="max-w-xs truncate">{alert.message}</TableCell>
                    <TableCell>{alert.agent_name || "System"}</TableCell>
                    <TableCell className="text-xs">
                      {alert.source.replace(/_/g, " ")}
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          )}
        </Card>
      </Grid>
    </div>
  );
}
