import type { FleetSummary } from "./types";

const BASE = "/api";

export async function fetchFleetSummary(): Promise<FleetSummary> {
  const res = await fetch(`${BASE}/fleet`);
  if (!res.ok) throw new Error(`Fleet API error: ${res.status}`);
  return res.json();
}

export async function refreshFleet(): Promise<void> {
  const res = await fetch(`${BASE}/fleet/refresh`, { method: "POST" });
  if (!res.ok) throw new Error(`Refresh error: ${res.status}`);
}
