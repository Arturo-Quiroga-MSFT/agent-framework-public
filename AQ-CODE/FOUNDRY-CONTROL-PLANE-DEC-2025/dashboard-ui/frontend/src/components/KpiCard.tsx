import {
  Card,
  Metric,
  Text,
  Flex,
  BadgeDelta,
  type DeltaType,
  type Color,
} from "@tremor/react";

interface Props {
  title: string;
  value: string;
  subtitle?: string;
  icon?: string;
  delta?: string;
  deltaType?: DeltaType;
  color?: Color;
}

export default function KpiCard({
  title,
  value,
  subtitle,
  icon,
  delta,
  deltaType = "unchanged",
  color = "blue",
}: Props) {
  return (
    <Card decoration="left" decorationColor={color}>
      <Flex justifyContent="between" alignItems="center">
        <Text>{title}</Text>
        {icon && <span className="text-xl">{icon}</span>}
      </Flex>
      <Metric className="mt-1">{value}</Metric>
      <Flex className="mt-2 space-x-2">
        {subtitle && (
          <Text className="truncate text-tremor-default">{subtitle}</Text>
        )}
        {delta && <BadgeDelta deltaType={deltaType}>{delta}</BadgeDelta>}
      </Flex>
    </Card>
  );
}
