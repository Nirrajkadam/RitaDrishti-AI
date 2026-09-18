import { PageHeader } from "@/components/dashboard/page-header";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { DataTable, type Column } from "@/components/dashboard/data-table";
import { Progress } from "@/components/ui/progress";
import EChart from "@/components/charts/echart";
import { CHART_COLORS } from "@/lib/chart-theme";
import { ShieldCheck, ShieldAlert, Scale, Eye } from "lucide-react";

const factors = [
  { label: "Data integrity", value: 88 },
  { label: "Model explainability", value: 76 },
  { label: "Compliance alignment", value: 91 },
  { label: "Human oversight", value: 82 },
  { label: "Bias & fairness", value: 69 },
];

const distributionBuckets = ["0–20", "21–40", "41–60", "61–80", "81–100"];
const distributionCounts = [12, 34, 168, 612, 1016];

interface Ranked {
  name: string;
  sector: string;
  score: number;
  trend: "up" | "down" | "flat";
}

const top: Ranked[] = [
  { name: "Meridian Capital Partners", sector: "Financial Services", score: 96, trend: "up" },
  { name: "Solaris Energy Grid", sector: "Renewables", score: 94, trend: "up" },
  { name: "Orbit Health Diagnostics", sector: "Healthcare", score: 91, trend: "flat" },
  { name: "Nimbus Cloud Services", sector: "Cloud Infra", score: 89, trend: "up" },
];

const bottom: Ranked[] = [
  { name: "Vantage Freight Ltd.", sector: "Logistics", score: 58, trend: "down" },
  { name: "Corelink Systems", sector: "Enterprise SaaS", score: 65, trend: "down" },
  { name: "Bharat Agrotech", sector: "Agriculture", score: 69, trend: "flat" },
  { name: "Fenix Retail Holdings", sector: "Retail", score: 71, trend: "down" },
];

const trendIcon = { up: "▲", down: "▼", flat: "—" } as const;
const trendColor = { up: "text-sight", down: "text-risk-critical", flat: "text-ink-600" } as const;

function rankedColumns(): Column<Ranked>[] {
  return [
    { key: "name", header: "Entity", render: (r) => <span className="font-medium">{r.name}</span> },
    { key: "sector", header: "Sector", render: (r) => <span className="text-ink-400">{r.sector}</span> },
    {
      key: "score",
      header: "Score",
      align: "right",
      render: (r) => <span className="mono-data text-ink-100">{r.score}</span>,
    },
    {
      key: "trend",
      header: "30d",
      align: "right",
      width: "60px",
      render: (r) => <span className={`text-xs ${trendColor[r.trend]}`}>{trendIcon[r.trend]}</span>,
    },
  ];
}

export default function TrustAnalyticsPage() {
  return (
    <div className="pb-10">
      <PageHeader
        title="Trust Analytics"
        description="How the trust score is composed, distributed, and moving across the portfolio."
        actions={<Button variant="outline" size="sm">Export analysis</Button>}
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3 px-6">
        <KpiCard label="Portfolio trust score" value="81.4" unit="/ 100" icon={ShieldCheck} delta={4.1} sparklineDesc="6-month change" />
        <KpiCard label="Entities below threshold" value="46" icon={ShieldAlert} delta={-11.2} sparklineDesc="threshold: 65" />
        <KpiCard label="Fairness parity index" value="0.94" icon={Scale} delta={1.5} sparklineDesc="demographic parity" />
        <KpiCard label="Model transparency" value="76.0" unit="%" icon={Eye} delta={2.3} sparklineDesc="explainability coverage" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-3 px-6 mt-3">
        <Card className="xl:col-span-2">
          <CardHeader>
            <div>
              <CardTitle>Score distribution</CardTitle>
              <CardDescription>1,842 entities bucketed by trust score</CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <EChart
              height={260}
              option={{
                xAxis: {
                  type: "category",
                  data: distributionBuckets,
                  axisLine: { lineStyle: { color: CHART_COLORS.line } },
                  axisTick: { show: false },
                },
                yAxis: {
                  type: "value",
                  splitLine: { lineStyle: { color: CHART_COLORS.line, type: "dashed" } },
                },
                series: [
                  {
                    type: "bar",
                    data: distributionCounts,
                    barWidth: "52%",
                    itemStyle: {
                      color: CHART_COLORS.signal,
                      borderRadius: [4, 4, 0, 0],
                    },
                  },
                ],
              }}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>Contributing factors</CardTitle>
              <CardDescription>Weighted composition of the score</CardDescription>
            </div>
          </CardHeader>
          <CardContent className="space-y-3.5">
            {factors.map((f) => (
              <div key={f.label}>
                <div className="flex items-center justify-between mb-1.5">
                  <span className="text-[13px] text-ink-100">{f.label}</span>
                  <span className="mono-data text-ink-400 text-xs">{f.value}</span>
                </div>
                <Progress value={f.value} className="h-1.5" />
              </div>
            ))}
          </CardContent>
        </Card>
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-3 px-6 mt-3">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>Highest trust</CardTitle>
              <CardDescription>Top performing entities this cycle</CardDescription>
            </div>
            <Badge variant="sight">clear</Badge>
          </CardHeader>
          <DataTable columns={rankedColumns()} rows={top} rowKey={(r) => r.name} />
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>Lowest trust</CardTitle>
              <CardDescription>Entities requiring review</CardDescription>
            </div>
            <Badge variant="critical">attention</Badge>
          </CardHeader>
          <DataTable columns={rankedColumns()} rows={bottom} rowKey={(r) => r.name} />
        </Card>
      </div>
    </div>
  );
}
