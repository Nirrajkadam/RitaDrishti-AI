import { Activity, Building2, ShieldCheck, Sparkles } from "lucide-react";
import { PageHeader } from "@/components/dashboard/page-header";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import EChart from "@/components/charts/echart";
import { CHART_COLORS } from "@/lib/chart-theme";
import { DataTable, type Column } from "@/components/dashboard/data-table";

const trustTrend = {
  months: ["Apr", "May", "Jun", "Jul", "Aug", "Sep"],
  portfolio: [71, 73, 74, 76, 78, 81],
  benchmark: [68, 68, 69, 70, 70, 71],
};

const riskDistribution = [
  { name: "Watch", value: 128, color: CHART_COLORS.watch },
  { name: "Elevated", value: 47, color: CHART_COLORS.elevated },
  { name: "Critical", value: 12, color: CHART_COLORS.critical },
];

interface Signal {
  id: string;
  entity: string;
  category: string;
  severity: "watch" | "elevated" | "critical";
  detected: string;
}

const signals: Signal[] = [
  { id: "SIG-4471", entity: "Vantage Freight Ltd.", category: "Model drift — pricing engine", severity: "critical", detected: "12 min ago" },
  { id: "SIG-4468", entity: "Corelink Systems", category: "Vendor concentration risk", severity: "elevated", detected: "41 min ago" },
  { id: "SIG-4462", entity: "Bharat Agrotech", category: "Sanctions list proximity", severity: "elevated", detected: "1 hr ago" },
  { id: "SIG-4455", entity: "Nimbus Cloud Services", category: "Data lineage gap", severity: "watch", detected: "2 hr ago" },
  { id: "SIG-4449", entity: "Orbit Health Diagnostics", category: "Explainability score dip", severity: "watch", detected: "3 hr ago" },
];

const severityVariant = {
  watch: "watch",
  elevated: "elevated",
  critical: "critical",
} as const;

const columns: Column<Signal>[] = [
  { key: "id", header: "Signal", width: "110px", render: (r) => <span className="mono-data text-ink-400">{r.id}</span> },
  { key: "entity", header: "Entity", render: (r) => <span className="font-medium">{r.entity}</span> },
  { key: "category", header: "Category", render: (r) => <span className="text-ink-400">{r.category}</span> },
  {
    key: "severity",
    header: "Severity",
    render: (r) => (
      <Badge variant={severityVariant[r.severity]} dot>
        {r.severity}
      </Badge>
    ),
  },
  { key: "detected", header: "Detected", align: "right", width: "110px", render: (r) => <span className="mono-data text-ink-600">{r.detected}</span> },
];

export default function HomeDashboard() {
  return (
    <div className="pb-10">
      <PageHeader
        title="Portfolio overview"
        description="Live posture across every monitored entity — trust, risk, and model health in one surface."
        actions={
          <>
            <Button variant="outline" size="sm">Last 6 months</Button>
            <Button size="sm">
              <Sparkles className="h-3.5 w-3.5" />
              Ask Copilot
            </Button>
          </>
        }
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3 px-6">
        <KpiCard label="Entities monitored" value="1,842" icon={Building2} delta={3.2} sparklineDesc="vs. last month" />
        <KpiCard label="Avg. trust score" value="81.4" unit="/ 100" icon={ShieldCheck} delta={4.1} sparklineDesc="portfolio-wide" />
        <KpiCard label="Active risk signals" value="187" icon={Activity} delta={-6.4} deltaGood={false} sparklineDesc="12 critical" />
        <KpiCard label="Model confidence" value="94.7" unit="%" icon={Sparkles} delta={0.8} sparklineDesc="inference avg." />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-3 px-6 mt-3">
        <Card className="xl:col-span-2">
          <CardHeader>
            <div>
              <CardTitle>Trust score trend</CardTitle>
              <CardDescription>Portfolio average vs. industry benchmark</CardDescription>
            </div>
            <div className="flex items-center gap-3 text-2xs text-ink-400">
              <span className="flex items-center gap-1.5"><span className="h-1.5 w-1.5 rounded-full bg-signal" />Portfolio</span>
              <span className="flex items-center gap-1.5"><span className="h-1.5 w-1.5 rounded-full bg-ink-600" />Benchmark</span>
            </div>
          </CardHeader>
          <CardContent>
            <EChart
              height={260}
              option={{
                xAxis: {
                  type: "category",
                  data: trustTrend.months,
                  axisLine: { lineStyle: { color: CHART_COLORS.line } },
                  axisTick: { show: false },
                },
                yAxis: {
                  type: "value",
                  min: 60,
                  max: 90,
                  splitLine: { lineStyle: { color: CHART_COLORS.line, type: "dashed" } },
                },
                series: [
                  {
                    name: "Portfolio",
                    type: "line",
                    data: trustTrend.portfolio,
                    smooth: true,
                    symbol: "circle",
                    symbolSize: 6,
                    lineStyle: { width: 2.5, color: CHART_COLORS.signal },
                    itemStyle: { color: CHART_COLORS.signal },
                    areaStyle: { color: "rgba(110,107,255,0.10)" },
                  },
                  {
                    name: "Benchmark",
                    type: "line",
                    data: trustTrend.benchmark,
                    smooth: true,
                    symbol: "none",
                    lineStyle: { width: 1.5, color: "#5B6270", type: "dashed" },
                  },
                ],
              }}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>Risk signal severity</CardTitle>
              <CardDescription>187 active across portfolio</CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <EChart
              height={260}
              option={{
                legend: { show: false },
                series: [
                  {
                    type: "pie",
                    radius: ["58%", "82%"],
                    center: ["50%", "48%"],
                    avoidLabelOverlap: false,
                    itemStyle: { borderColor: "#191C20", borderWidth: 2 },
                    label: { show: false },
                    data: riskDistribution.map((d) => ({
                      name: d.name,
                      value: d.value,
                      itemStyle: { color: d.color },
                    })),
                  },
                ],
              }}
            />
            <div className="flex justify-center gap-4 -mt-2">
              {riskDistribution.map((d) => (
                <div key={d.name} className="text-center">
                  <div className="text-sm font-semibold tabular" style={{ color: d.color }}>
                    {d.value}
                  </div>
                  <div className="text-2xs text-ink-600">{d.name}</div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      <div className="px-6 mt-3">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>Latest risk signals</CardTitle>
              <CardDescription>Newest detections across all monitored entities</CardDescription>
            </div>
            <Button variant="ghost" size="sm">View risk center</Button>
          </CardHeader>
          <DataTable columns={columns} rows={signals} rowKey={(r) => r.id} />
        </Card>
      </div>
    </div>
  );
}
