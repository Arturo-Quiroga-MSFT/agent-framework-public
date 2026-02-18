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
  TextInput,
  Select,
  SelectItem,
  Text,
} from "@tremor/react";
import { useState, useMemo } from "react";
import type { AgentMetrics } from "../types";

interface Props {
  agents: AgentMetrics[];
}

const STATUS_BADGE: Record<string, { color: "emerald" | "amber" | "red" | "gray"; icon: string }> = {
  healthy: { color: "emerald", icon: "✅" },
  warning: { color: "amber", icon: "⚠️" },
  critical: { color: "red", icon: "🔴" },
  unknown: { color: "gray", icon: "❓" },
};

type SortKey = "health" | "name" | "runs" | "error" | "cost" | "latency";

export default function AgentsTable({ agents }: Props) {
  const [search, setSearch] = useState("");
  const [statusFilter, setStatusFilter] = useState("all");
  const [sortBy, setSortBy] = useState<SortKey>("health");

  const filtered = useMemo(() => {
    let list = agents;

    if (statusFilter !== "all") {
      list = list.filter((a) => a.status === statusFilter);
    }

    if (search) {
      const q = search.toLowerCase();
      list = list.filter((a) => a.agent_name.toLowerCase().includes(q));
    }

    const sortFns: Record<SortKey, (a: AgentMetrics, b: AgentMetrics) => number> = {
      health: (a, b) => b.health_score - a.health_score,
      name: (a, b) => a.agent_name.localeCompare(b.agent_name),
      runs: (a, b) => b.total_runs - a.total_runs,
      error: (a, b) => b.error_rate - a.error_rate,
      cost: (a, b) => b.estimated_cost_usd - a.estimated_cost_usd,
      latency: (a, b) => b.avg_latency_ms - a.avg_latency_ms,
    };

    return [...list].sort(sortFns[sortBy]);
  }, [agents, search, statusFilter, sortBy]);

  return (
    <Card>
      <Title>📋 Agent Inventory ({agents.length} agents)</Title>

      {/* Filters */}
      <div className="mt-4 flex flex-wrap items-end gap-4">
        <div className="w-64">
          <Text className="mb-1">Search</Text>
          <TextInput
            placeholder="Filter by agent name…"
            value={search}
            onValueChange={setSearch}
          />
        </div>
        <div className="w-40">
          <Text className="mb-1">Status</Text>
          <Select value={statusFilter} onValueChange={setStatusFilter}>
            <SelectItem value="all">All</SelectItem>
            <SelectItem value="healthy">Healthy</SelectItem>
            <SelectItem value="warning">Warning</SelectItem>
            <SelectItem value="critical">Critical</SelectItem>
          </Select>
        </div>
        <div className="w-40">
          <Text className="mb-1">Sort by</Text>
          <Select value={sortBy} onValueChange={(v) => setSortBy(v as SortKey)}>
            <SelectItem value="health">Health Score</SelectItem>
            <SelectItem value="name">Name</SelectItem>
            <SelectItem value="runs">Runs</SelectItem>
            <SelectItem value="error">Error Rate</SelectItem>
            <SelectItem value="cost">Cost</SelectItem>
            <SelectItem value="latency">Latency</SelectItem>
          </Select>
        </div>
      </div>

      {/* Table */}
      <Table className="mt-4">
        <TableHead>
          <TableRow>
            <TableHeaderCell>Status</TableHeaderCell>
            <TableHeaderCell>Agent Name</TableHeaderCell>
            <TableHeaderCell>Model</TableHeaderCell>
            <TableHeaderCell>Ver</TableHeaderCell>
            <TableHeaderCell>Health</TableHeaderCell>
            <TableHeaderCell>Runs (24h)</TableHeaderCell>
            <TableHeaderCell>Error %</TableHeaderCell>
            <TableHeaderCell>Avg Latency</TableHeaderCell>
            <TableHeaderCell>Tokens</TableHeaderCell>
            <TableHeaderCell>Cost</TableHeaderCell>
            <TableHeaderCell>Tools</TableHeaderCell>
          </TableRow>
        </TableHead>
        <TableBody>
          {filtered.map((a) => {
            const badge = STATUS_BADGE[a.status] ?? STATUS_BADGE.unknown;
            const errColor =
              a.error_rate > 0.1
                ? "red"
                : a.error_rate > 0.05
                  ? "amber"
                  : "emerald";

            return (
              <TableRow key={a.agent_id}>
                <TableCell>
                  <Badge color={badge.color}>{badge.icon} {a.status}</Badge>
                </TableCell>
                <TableCell className="font-semibold">{a.agent_name}</TableCell>
                <TableCell>
                  <code className="text-xs bg-gray-100 rounded px-1 py-0.5">
                    {a.model}
                  </code>
                </TableCell>
                <TableCell>v{a.agent_version}</TableCell>
                <TableCell>
                  <Badge color={badge.color}>{a.health_score.toFixed(0)}%</Badge>
                </TableCell>
                <TableCell>{a.total_runs.toLocaleString()}</TableCell>
                <TableCell>
                  <Badge color={errColor}>{(a.error_rate * 100).toFixed(1)}%</Badge>
                </TableCell>
                <TableCell>{a.avg_latency_ms.toFixed(0)}ms</TableCell>
                <TableCell>{a.total_tokens.toLocaleString()}</TableCell>
                <TableCell>${a.estimated_cost_usd.toFixed(4)}</TableCell>
                <TableCell>
                  <span className="text-xs text-tremor-content-subtle truncate max-w-[120px] inline-block">
                    {a.tools.join(", ") || "—"}
                  </span>
                </TableCell>
              </TableRow>
            );
          })}
        </TableBody>
      </Table>
      {filtered.length === 0 && (
        <Text className="mt-4 text-center text-tremor-content-subtle py-8">
          No agents match the current filters.
        </Text>
      )}
    </Card>
  );
}
