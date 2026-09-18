import { PageHeader } from "@/components/dashboard/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { DataTable, type Column } from "@/components/dashboard/data-table";
import { FileText, Download, CalendarClock, Plus } from "lucide-react";
import EChart from "@/components/charts/echart";
import { CHART_COLORS } from "@/lib/chart-theme";

interface Report {
  name: string;
  type: string;
  period: string;
  generated: string;
  status: "ready" | "scheduled" | "processing";
}

const reports: Report[] = [
  { name: "Q3 Portfolio Risk Summary", type: "Board brief", period: "Jul – Sep 2026", generated: "2026-09-17", status: "ready" },
  { name: "Trust Analytics Deep Dive", type: "Analytical", period: "Aug 2026", generated: "2026-09-10", status: "ready" },
  { name: "Logistics Sector Exposure", type: "Sector review", period: "Sep 2026", generated: "2026-09-18", status: "processing" },
  { name: "Monthly Compliance Attestation", type: "Regulatory", period: "Sep 2026", generated: "—", status: "scheduled" },
  { name: "Vendor Concentration Review", type: "Risk assessment", period: "Q3 2026", generated: "2026-09-05", status: "ready" },
];

const statusVariant = { ready: "sight", scheduled: "neutral", processing: "watch" } as const;

const columns: Column<Report>[] = [
  {
    key: "name",
    header: "Report",
    render: (r) => (
      <div className="flex items-center gap-2.5">
        <FileText className="h-3.5 w-3.5 text-ink-600" />
        <span className="font-medium">{r.name}</span>
      </div>
    ),
  },
  { key: "type", header: "Type", render: (r) => <span className="text-ink-400">{r.type}</span> },
  { key: "period", header: "Period", render: (r) => <span className="mono-data text-ink-400">{r.period}</span> },
  { key: "generated", header: "Generated", render: (r) => <span className="mono-data text-ink-600">{r.generated}</span> },
  {
    key: "status",
    header: "Status",
    render: (r) => <Badge variant={statusVariant[r.status]} dot>{r.status}</Badge>,
  },
  {
    key: "action",
    header: "",
    align: "right",
    render: (r) =>
      r.status === "ready" ? (
        <Button variant="ghost" size="sm">
          <Download className="h-3.5 w-3.5" />
        </Button>
      ) : (
        <span className="text-ink-600 text-2xs">—</span>
      ),
  },
];

export default function ExecutiveReportsPage() {
  return (
    <div className="pb-10">
      <PageHeader
        title="Executive Reports"
        description="Board-ready summaries generated from live portfolio, trust, and risk data."
        actions={
          <>
            <Button variant="outline" size="sm">
              <CalendarClock className="h-3.5 w-3.5" />
              Schedule
            </Button>
            <Button size="sm">
              <Plus className="h-3.5 w-3.5" />
              Generate report
            </Button>
          </>
        }
      />

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-3 px-6">
        <Card className="xl:col-span-2">
          <CardHeader>
            <div>
              <CardTitle>Report library</CardTitle>
              <CardDescription>24 reports generated this quarter</CardDescription>
            </div>
          </CardHeader>
          <DataTable columns={columns} rows={reports} rowKey={(r) => r.name} />
        </Card>

        <Card>
          <CardHeader>
            <div>
              <CardTitle>Q3 Portfolio Risk Summary</CardTitle>
              <CardDescription>Preview · 12 pages</CardDescription>
            </div>
          </CardHeader>
          <CardContent className="space-y-4">
            <EChart
              height={160}
              option={{
                grid: { left: 0, right: 0, top: 8, bottom: 0 },
                xAxis: { show: false, type: "category", data: ["Jul", "Aug", "Sep"] },
                yAxis: { show: false, type: "value" },
                series: [
                  {
                    type: "bar",
                    data: [74, 78, 81],
                    barWidth: "40%",
                    itemStyle: { color: CHART_COLORS.signal, borderRadius: [3, 3, 0, 0] },
                  },
                ],
              }}
            />
            <div className="space-y-2 text-2xs text-ink-400 leading-relaxed">
              <p>
                Portfolio trust rose from 74 to 81 across the quarter, driven by
                improved compliance alignment in the Financial Services and
                Renewables sectors.
              </p>
              <p>
                Twelve entities remain in critical risk status, concentrated in
                Logistics and Enterprise SaaS, primarily linked to model drift
                and vendor concentration signals.
              </p>
            </div>
            <div className="hairline-top pt-3 flex gap-2">
              <Button variant="outline" size="sm" className="flex-1">Preview</Button>
              <Button size="sm" className="flex-1">
                <Download className="h-3.5 w-3.5" />
                Download PDF
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
