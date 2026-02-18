import { useState, useEffect, useCallback } from "react";
import {
  TabGroup,
  TabList,
  Tab,
  TabPanels,
  TabPanel,
  Flex,
  Text,
  Badge,
  Button,
} from "@tremor/react";
import type { FleetSummary } from "./types";
import { fetchFleetSummary, refreshFleet } from "./api";
import Overview from "./components/Overview";
import AgentsTable from "./components/AgentsTable";
import AlertsPanel from "./components/AlertsPanel";
import ComplianceView from "./components/ComplianceView";
import CostAnalysis from "./components/CostAnalysis";

export default function App() {
  const [data, setData] = useState<FleetSummary | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [lastRefresh, setLastRefresh] = useState<string>("");

  const load = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);
      const summary = await fetchFleetSummary();
      setData(summary);
      setLastRefresh(new Date().toLocaleTimeString());
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Failed to load fleet data");
    } finally {
      setLoading(false);
    }
  }, []);

  const handleRefresh = useCallback(async () => {
    try {
      await refreshFleet();
    } catch {
      // ignore — we'll refetch
    }
    await load();
  }, [load]);

  useEffect(() => {
    load();
  }, [load]);

  return (
    <div className="min-h-screen bg-tremor-background">
      {/* Navbar */}
      <header className="sticky top-0 z-50 border-b border-tremor-border bg-tremor-background-emphasis">
        <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-3">
          <Flex className="gap-3" justifyContent="start" alignItems="center">
            <span className="text-2xl">🎛️</span>
            <div>
              <h1 className="text-lg font-bold text-white">
                Microsoft Foundry Control Plane
              </h1>
              <p className="text-xs text-tremor-content-inverted/60">
                Fleet Health Dashboard
              </p>
            </div>
          </Flex>
          <Flex className="gap-3" justifyContent="end" alignItems="center">
            {data && (
              <Badge color={data.data_source === "azure" ? "emerald" : "amber"}>
                {data.data_source === "azure" ? "🟢 Azure" : "🟡 Demo"}
              </Badge>
            )}
            {lastRefresh && (
              <Text className="text-xs text-tremor-content-inverted/60">
                {lastRefresh}
              </Text>
            )}
            <Button
              size="xs"
              variant="secondary"
              loading={loading}
              onClick={handleRefresh}
            >
              ↻ Refresh
            </Button>
          </Flex>
        </div>
      </header>

      {/* Main content */}
      <main className="mx-auto max-w-7xl px-4 py-6">
        {error && (
          <div className="mb-6 rounded-lg border border-red-200 bg-red-50 p-4 text-red-700">
            {error}
          </div>
        )}

        {loading && !data && (
          <div className="flex items-center justify-center py-32">
            <Text className="text-lg animate-pulse">
              Loading fleet data…
            </Text>
          </div>
        )}

        {data && (
          <TabGroup>
            <TabList variant="solid" className="mb-6">
              <Tab>📊 Overview</Tab>
              <Tab>🤖 Agents</Tab>
              <Tab>🚨 Alerts</Tab>
              <Tab>🛡️ Compliance</Tab>
              <Tab>💰 Cost Analysis</Tab>
            </TabList>
            <TabPanels>
              <TabPanel>
                <Overview data={data} />
              </TabPanel>
              <TabPanel>
                <AgentsTable agents={data.agents} />
              </TabPanel>
              <TabPanel>
                <AlertsPanel data={data} />
              </TabPanel>
              <TabPanel>
                <ComplianceView data={data} />
              </TabPanel>
              <TabPanel>
                <CostAnalysis data={data} />
              </TabPanel>
            </TabPanels>
          </TabGroup>
        )}
      </main>

      {/* Footer */}
      <footer className="border-t border-tremor-border py-4 mt-12">
        <div className="mx-auto max-w-7xl px-4 text-center text-xs text-tremor-content-subtle">
          <div className="flex flex-wrap justify-center gap-4 mb-2">
            <a href="https://portal.azure.com" target="_blank" rel="noopener noreferrer" className="hover:underline">Azure Portal</a>
            <a href="https://ai.azure.com" target="_blank" rel="noopener noreferrer" className="hover:underline">Foundry Portal</a>
            <a href="https://aka.ms/amg/dash/af-agent" target="_blank" rel="noopener noreferrer" className="hover:underline">Grafana Agent Dashboard</a>
            <a href="https://aka.ms/amg/dash/af-workflow" target="_blank" rel="noopener noreferrer" className="hover:underline">Grafana Workflow Dashboard</a>
          </div>
          <p>Microsoft Foundry Control Plane • February 2026</p>
        </div>
      </footer>
    </div>
  );
}
