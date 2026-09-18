import { Filter, MapPin, Users, TrendingUp } from "lucide-react";
import { PageHeader } from "@/components/dashboard/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DataTable, type Column } from "@/components/dashboard/data-table";
import { Progress } from "@/components/ui/progress";
import EChart from "@/components/charts/echart";
import { CHART_COLORS } from "@/lib/chart-theme";

interface Company {
  name: string;
  sector: string;
  hq: string;
  trust: number;
  risk: "watch" | "elevated" | "critical" | "none";
  revenue: string;
  employees: string;
}

const companies: Company[] = [
  { name: "Vantage Freight Ltd.", sector: "Logistics", hq: "Pune, IN", trust: 58, risk: "critical", revenue: "₹1,240 Cr", employees: "6,200" },
  { name: "Corelink Systems", sector: "Enterprise SaaS", hq: "Bengaluru, IN", trust: 72, risk: "elevated", revenue: "₹640 Cr", employees: "2,150" },
  { name: "Bharat Agrotech", sector: "Agriculture", hq: "Nashik, IN", trust: 76, risk: "elevated", revenue: "₹410 Cr", employees: "1,480" },
  { name: "Nimbus Cloud Services", sector: "Cloud Infra", hq: "Hyderabad, IN", trust: 84, risk: "watch", revenue: "₹980 Cr", employees: "3,900" },
  { name: "Orbit Health Diagnostics", sector: "Healthcare", hq: "Mumbai, IN", trust: 88, risk: "watch", revenue: "₹720 Cr", employees: "2,760" },
  { name: "Solaris Energy Grid", sector: "Renewables", hq: "Ahmedabad, IN", trust: 91, risk: "none", revenue: "₹1,860 Cr", employees: "4,300" },
  { name: "Meridian Capital Partners", sector: "Financial Services", hq: "Mumbai, IN", trust: 93, risk: "none", revenue: "₹2,100 Cr", employees: "980" },
];

const riskVariant = { watch: "watch", elevated: "elevated", critical: "critical", none: "sight" } as const;

const columns: Column<Company>[] = [
  {
    key: "name",
    header: "Entity",
    render: (r) => (
      <div>
        <div className="font-medium text-ink-100">{r.name}</div>
        <div className="text-2xs text-ink-600 flex items-center gap-1 mt-0.5">
          <MapPin className="h-2.5 w-2.5" /> {r.hq}
        </div>
      </div>
    ),
  },
  { key: "sector", header: "Sector", render: (r) => <span className="text-ink-400">{r.sector}</span> },
  {
    key: "trust",
    header: "Trust score",
    width: "160px",
    render: (r) => (
      <div className="flex items-center gap-2 w-32">
        <Progress value={r.trust} className="h-1" />
        <span className="mono-data text-ink-100 w-7 text-right">{r.trust}</span>
      </div>
    ),
  },
  {
    key: "risk",
    header: "Risk",
    render: (r) => (
      <Badge variant={riskVariant[r.risk]} dot>
        {r.risk === "none" ? "clear" : r.risk}
      </Badge>
    ),
  },
  { key: "revenue", header: "Revenue (FY25)", align: "right", render: (r) => <span className="mono-data text-ink-100">{r.revenue}</span> },
  { key: "employees", header: "Headcount", align: "right", render: (r) => <span className="mono-data text-ink-400">{r.employees}</span> },
];

export default function CompanyIntelligencePage() {
  return (
    <div className="pb-10">
      <PageHeader
        title="Company Intelligence"
        description="Structured profiles built from filings, market signals, and model-derived risk indicators."
        actions={
          <>
            <Button variant="outline" size="sm">
              <Filter className="h-3.5 w-3.5" />
              Filters
            </Button>
            <Button size="sm">Add entity</Button>
          </>
        }
      />

      <div className="grid grid-cols-1 2xl:grid-cols-3 gap-3 px-6">
        <Card className="2xl:col-span-2">
          <CardHeader>
            <div>
              <CardTitle>Monitored entities</CardTitle>
              <CardDescription>1,842 total · sorted by risk priority</CardDescription>
            </div>
          </CardHeader>
          <DataTable columns={columns} rows={companies} rowKey={(r) => r.name} />
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>Vantage Freight Ltd.</CardTitle>
              <CardDescription>Logistics · Pune, IN · est. 2011</CardDescription>
            </div>
            <Badge variant="critical" dot>critical</Badge>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-3">
              <div className="panel-raised px-3 py-2.5">
                <div className="text-2xs text-ink-600 flex items-center gap-1"><TrendingUp className="h-3 w-3" />Revenue</div>
                <div className="mono-data text-ink-100 mt-1">₹1,240 Cr</div>
              </div>
              <div className="panel-raised px-3 py-2.5">
                <div className="text-2xs text-ink-600 flex items-center gap-1"><Users className="h-3 w-3" />Headcount</div>
                <div className="mono-data text-ink-100 mt-1">6,200</div>
              </div>
            </div>

            <div>
              <div className="text-2xs font-medium text-ink-600 mb-2">Intelligence dimensions</div>
              <EChart
                height={220}
                option={{
                  radar: {
                    indicator: [
                      { name: "Financial health", max: 100 },
                      { name: "Governance", max: 100 },
                      { name: "Data integrity", max: 100 },
                      { name: "Market position", max: 100 },
                      { name: "Compliance", max: 100 },
                    ],
                    axisName: { color: CHART_COLORS.ink, fontSize: 10 },
                    splitLine: { lineStyle: { color: CHART_COLORS.line } },
                    axisLine: { lineStyle: { color: CHART_COLORS.line } },
                    splitArea: { show: false },
                  },
                  series: [
                    {
                      type: "radar",
                      data: [
                        {
                          value: [61, 48, 55, 74, 52],
                          areaStyle: { color: "rgba(229,72,77,0.15)" },
                          lineStyle: { color: CHART_COLORS.critical, width: 2 },
                          itemStyle: { color: CHART_COLORS.critical },
                        },
                      ],
                    },
                  ],
                }}
              />
            </div>

            <div className="text-2xs text-ink-400 leading-relaxed">
              Trust score dropped 14 points after Q3 filing showed a fuel-cost
              hedge mismatch. Model flags rising counterparty concentration in
              the north corridor route network.
            </div>
            <Button variant="outline" size="sm" className="w-full">
              Open full profile
            </Button>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
