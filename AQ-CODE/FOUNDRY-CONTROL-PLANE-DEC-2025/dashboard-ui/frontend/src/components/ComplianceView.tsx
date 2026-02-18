import {
  Card,
  Title,
  Text,
  Grid,
  Metric,
  Badge,
  Callout,
} from "@tremor/react";
import type { FleetSummary, ComplianceIssue } from "../types";

interface Props {
  data: FleetSummary;
}

export default function ComplianceView({ data }: Props) {
  const pct =
    data.total_agents > 0
      ? ((data.compliant_agents / data.total_agents) * 100).toFixed(0)
      : "0";
  const pctColor =
    Number(pct) >= 80 ? "emerald" : Number(pct) >= 50 ? "amber" : "red";

  return (
    <div className="space-y-6">
      <Grid numItemsSm={1} numItemsLg={2} className="gap-6">
        {/* Score card */}
        <Card decoration="top" decorationColor={pctColor}>
          <Text className="text-center">Compliance Score</Text>
          <Metric className="text-center mt-2 text-5xl">{pct}%</Metric>
          <div className="mt-4 flex justify-center gap-8">
            <div className="text-center">
              <Metric className="text-emerald-500">{data.compliant_agents}</Metric>
              <Text>Compliant</Text>
            </div>
            <div className="text-center">
              <Metric className="text-red-500">{data.non_compliant_agents}</Metric>
              <Text>Non-Compliant</Text>
            </div>
          </div>
        </Card>

        {/* Rules overview */}
        <Card>
          <Title>📋 Compliance Rules</Title>
          <div className="mt-4 space-y-3">
            <div>
              <Text className="font-semibold text-red-600">🔴 Critical Rules (Required)</Text>
              <ul className="ml-5 mt-1 list-disc text-sm text-tremor-content space-y-1">
                <li><strong>Instructions Required</strong> — All agents must have a system prompt</li>
                <li><strong>Model Governance</strong> — Only approved models allowed</li>
              </ul>
            </div>
            <div>
              <Text className="font-semibold text-amber-600">🟡 Warnings (Recommended)</Text>
              <ul className="ml-5 mt-1 list-disc text-sm text-tremor-content space-y-1">
                <li><strong>Content Safety</strong> — High-risk tools should have safety instructions</li>
                <li><strong>Metadata</strong> — Agents should have governance metadata</li>
              </ul>
            </div>
          </div>
        </Card>
      </Grid>

      {/* Violations */}
      <Card>
        <Title>🔴 Policy Violations ({data.compliance_violations.length})</Title>
        {data.compliance_violations.length === 0 ? (
          <Callout title="All Clear" color="emerald" className="mt-4">
            No policy violations! All agents meet required compliance standards.
          </Callout>
        ) : (
          <div className="mt-4 space-y-3">
            {data.compliance_violations.map((v: ComplianceIssue, i: number) => (
              <Callout key={i} title={v.agent_name} color="red">
                <Text className="font-medium">{v.message}</Text>
                <Text className="mt-1 text-sm">
                  💡 <strong>Recommendation:</strong> {v.recommendation}
                </Text>
                <Badge color="red" className="mt-2">{v.rule}</Badge>
              </Callout>
            ))}
          </div>
        )}
      </Card>

      {/* Warnings */}
      <Card>
        <Title>🟡 Compliance Warnings ({data.compliance_warnings.length})</Title>
        {data.compliance_warnings.length === 0 ? (
          <Text className="mt-4">No additional warnings. All recommended practices are followed.</Text>
        ) : (
          <div className="mt-4 space-y-3">
            {data.compliance_warnings.map((w: ComplianceIssue, i: number) => (
              <Callout key={i} title={w.agent_name} color="amber">
                <Text>{w.message}</Text>
                <Text className="mt-1 text-sm">
                  💡 <strong>Recommendation:</strong> {w.recommendation}
                </Text>
              </Callout>
            ))}
          </div>
        )}
      </Card>

      {/* Model governance reference */}
      <Grid numItemsSm={1} numItemsLg={2} className="gap-6">
        <Card>
          <Title>✅ Approved Models</Title>
          <pre className="mt-3 rounded bg-gray-50 p-3 text-xs leading-relaxed">
{`gpt-4o, gpt-4o-mini
gpt-4.1, gpt-4.1-mini, gpt-4.1-nano
gpt-5-chat, gpt-5.1-chat
o1, o1-mini, o1-preview, o3-mini`}
          </pre>
        </Card>
        <Card>
          <Title>❌ Deprecated Models</Title>
          <pre className="mt-3 rounded bg-red-50 p-3 text-xs text-red-600 leading-relaxed">
{`gpt-3.5-turbo, gpt-3.5-turbo-16k
gpt-4-32k, gpt-4-vision-preview
text-davinci-003, text-davinci-002`}
          </pre>
        </Card>
      </Grid>
    </div>
  );
}
