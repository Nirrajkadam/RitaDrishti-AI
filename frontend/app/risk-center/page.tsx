import { PageHeader } from "@/components/dashboard/page-header";
import { KpiCard } from "@/components/dashboard/kpi-card";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { DataTable, type Column } from "@/components/dashboard/data-table";
import EChart from "@/components/charts/echart";
import { CHART_COLORS } from "@/lib/chart-theme";
import { AlertTriangle, Flame, Clock, ShieldOff } from "lucide-react";

const categories = ["Credit", "Compliance", "Operational", "Model", "Cyber", "Reputational"];
const units = ["Logistics", "Retail", "Financial Svcs", "Healthcare", "Energy"];

// value = [unitIndex, categoryIndex, severity 0-4]
const heat: [number, number, number][] = [
  [0, 0, 3], [0, 1, 2], [0, 2, 4], [0, 3, 1], [0, 4, 1], [0, 5, 2],
  [1, 0, 2], [1, 1, 1], [1, 2, 2], [1, 3, 0], [1, 4, 2], [1, 5, 3],
  [2, 0, 1], [2, 1, 3], [2, 2, 1], [2, 3, 2], [2, 4, 4], [2, 5, 1],
  [3, 0, 0], [3, 1, 1], [3, 2, 1], [3, 3, 1], [3, 4, 1], [3, 5, 0],
  [4, 0, 2], [4, 1, 1], [4, 2, 2], [4, 3, 0], [4, 4, 1], [4, 5, 1],
];

const trendDays = ["Sep 12", "Sep 13", "Sep 14", "Sep 15", "Sep 16", "Sep 17", "Sep 18"];
const watchSeries = [96, 101, 110, 104, 118, 122, 128];
const elevatedSeries = [31, 34, 30, 38, 41, 44, 47];
const criticalSeries = [6, 7, 9, 8, 10, 11, 12];

interface Incident {
  id: string;
  entity: string;
  category: string;
  severity: "watch" | "elevated" | "critical";
  owner: string;
  age: string;
}

const incidents: Incident[] = [
  { id: "INC-2231", entity: "Vantage Freight Ltd.", category: "Model drift", severity: "critical", owner: "Risk Ops", age: "2h" },
  { id: "INC-2229", entity: "Corelink Systems", category: "Vendor concentration", severity: "elevated", owner: "Third-Party Risk", age: "5h" },
  { id: "INC-2224", entity: "Bharat Agrotech", category: "Sanctions proximity", severity: "elevated", owner: "Compliance", age: "9h" },
  { id: "INC-2218", entity: "Nimbus Cloud Services", category: "Data lineage gap", severity: "watch", owner: "Data Governance", age: "1d" },
  { id: "INC-2211", entity: "Fenix Retail Holdings", category: "Chargeback spike", severity: "watch", owner: "Fraud Ops", age: "1d" },
  { id: "INC-2204", entity: "Orbit Health Diagnostics", category: "Explainability dip", severity: "watch", owner: "Model Risk", age: "2d" },
];

const severityVariant = { watch: "watch", elevated: "elevated", critical: "critical" } as const;

const columns: Column<Incident>[] = [
  { key: "id", header: "Incident", width: "100px", render: (r) => <span className="mono-data text-ink-400">{r.id}</span> },
  { key: "entity", header: "Entity", render: (r) => <span className="font-medium">{r.entity}</span> },
  { key: "category", header: "Category", render: (r) => <span className="text-ink-400">{r.category}</span> },
  { key: "severity", header: "Severity", render: (r) => <Badge variant={severityVariant[r.severity]} dot>{r.severity}</Badge> },
  { key: "owner", header: "Owner", render: (r) => <span className="text-ink-400">{r.owner}</span> },
  { key: "age", header: "Age", align: "right", width: "70px", render: (r) => <span className="mono-data text-ink-600">{r.age}</span> },
];

const severityColorScale = ["#22262B", "#3A3320", CHART_COLORS.watch, CHART_COLORS.elevated, CHART_COLORS.critical];

export default function RiskCenterPage() {
  return (
    <div className="pb-10">
      <PageHeader
        title="Risk Center"
        description="Real-time monitoring of active risk signals across categories and business units."
        actions={
          <>
            <Button variant="outline" size="sm">Escalation rules</Button>
            <Button size="sm" variant="destructive">
              <Flame className="h-3.5 w-3.5" />
              12 critical
            </Button>
          </>
        }
      />

      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-4 gap-3 px-6">
        <KpiCard label="Critical signals" value="12" icon={AlertTriangle} delta={9.1} deltaGood={false} sparklineDesc="requires action" />
        <KpiCard label="Elevated signals" value="47" icon={ShieldOff} delta={7.0} deltaGood={false} sparklineDesc="under review" />
        <KpiCard label="Watch signals" value="128" icon={Flame} delta={4.9} deltaGood={false} sparklineDesc="auto-triaged" />
        <KpiCard label="Median time to triage" value="18" unit="min" icon={Clock} delta={-22.0} sparklineDesc="week over week" />
      </div>

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-3 px-6 mt-3">
        <Card className="xl:col-span-2">
          <CardHeader>
            <div>
              <CardTitle>Risk heatmap</CardTitle>
              <CardDescription>Signal concentration by business unit and category</CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <EChart
              height={280}
              option={{
                grid: { left: 100, right: 20, top: 20, bottom: 30 },
                xAxis: {
                  type: "category",
                  data: categories,
                  splitArea: { show: true },
                  axisLine: { lineStyle: { color: CHART_COLORS.line } },
                  axisTick: { show: false },
                },
                yAxis: {
                  type: "category",
                  data: units,
                  splitArea: { show: true },
                  axisLine: { lineStyle: { color: CHART_COLORS.line } },
                },
                visualMap: { show: false, min: 0, max: 4 },
                series: [
                  {
                    type: "heatmap",
                    data: heat.map(([u, c, s]) => [c, u, s]),
                    itemStyle: { borderColor: "#0A0B0D", borderWidth: 3 },
                    emphasis: { itemStyle: { borderColor: CHART_COLORS.signal, borderWidth: 1.5 } },
                  } as any,
                ],
                color: severityColorScale,
              }}
            />
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>7-day signal trend</CardTitle>
              <CardDescription>New detections by severity</CardDescription>
            </div>
          </CardHeader>
          <CardContent>
            <EChart
              height={280}
              option={{
                legend: {
                  top: 0,
                  right: 0,
                  itemWidth: 8,
                  itemHeight: 8,
                  textStyle: { color: CHART_COLORS.ink, fontSize: 10 },
                },
                xAxis: {
                  type: "category",
                  data: trendDays,
                  axisLine: { lineStyle: { color: CHART_COLORS.line } },
                  axisTick: { show: false },
                  axisLabel: { fontSize: 9 },
                },
                yAxis: { type: "value", splitLine: { lineStyle: { color: CHART_COLORS.line, type: "dashed" } } },
                series: [
                  { name: "Watch", type: "line", stack: "total", areaStyle: {}, data: watchSeries, symbol: "none", lineStyle: { color: CHART_COLORS.watch }, itemStyle: { color: CHART_COLORS.watch } },
                  { name: "Elevated", type: "line", stack: "total", areaStyle: {}, data: elevatedSeries, symbol: "none", lineStyle: { color: CHART_COLORS.elevated }, itemStyle: { color: CHART_COLORS.elevated } },
                  { name: "Critical", type: "line", stack: "total", areaStyle: {}, data: criticalSeries, symbol: "none", lineStyle: { color: CHART_COLORS.critical }, itemStyle: { color: CHART_COLORS.critical } },
                ],
              }}
            />
          </CardContent>
        </Card>
      </div>

      <div className="px-6 mt-3">
        <Card>
          <CardHeader>
            <div>
              <CardTitle>Open incidents</CardTitle>
              <CardDescription>Assigned and awaiting resolution</CardDescription>
            </div>
            <Button variant="ghost" size="sm">View all 62</Button>
          </CardHeader>
          <DataTable columns={columns} rows={incidents} rowKey={(r) => r.id} />
        </Card>
      </div>
    </div>
  );
}
