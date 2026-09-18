import { PageHeader } from "@/components/dashboard/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import EChart from "@/components/charts/echart";
import { CHART_COLORS } from "@/lib/chart-theme";
import { Maximize2, Layers } from "lucide-react";

const categories = [
  { name: "Company", color: CHART_COLORS.signal },
  { name: "Person", color: CHART_COLORS.sight },
  { name: "Risk signal", color: CHART_COLORS.critical },
  { name: "Regulatory body", color: CHART_COLORS.watch },
  { name: "Contract", color: "#5B6270" },
];

const nodes = [
  { id: "0", name: "Vantage Freight Ltd.", category: 0, symbolSize: 46 },
  { id: "1", name: "R. Malhotra (CEO)", category: 1, symbolSize: 26 },
  { id: "2", name: "S. Iyer (CFO)", category: 1, symbolSize: 24 },
  { id: "3", name: "Model drift — pricing engine", category: 2, symbolSize: 30 },
  { id: "4", name: "Sanctions proximity", category: 2, symbolSize: 22 },
  { id: "5", name: "SEBI", category: 3, symbolSize: 24 },
  { id: "6", name: "Corelink Systems", category: 0, symbolSize: 34 },
  { id: "7", name: "Master Freight Agreement", category: 4, symbolSize: 20 },
  { id: "8", name: "Bharat Agrotech", category: 0, symbolSize: 30 },
  { id: "9", name: "K. Rao (Board member)", category: 1, symbolSize: 22 },
  { id: "10", name: "Nimbus Cloud Services", category: 0, symbolSize: 28 },
  { id: "11", name: "Data lineage gap", category: 2, symbolSize: 20 },
  { id: "12", name: "RBI", category: 3, symbolSize: 22 },
];

const links = [
  { source: "0", target: "1" },
  { source: "0", target: "2" },
  { source: "0", target: "3" },
  { source: "0", target: "4" },
  { source: "0", target: "5" },
  { source: "0", target: "7" },
  { source: "6", target: "7" },
  { source: "0", target: "9" },
  { source: "9", target: "8" },
  { source: "8", target: "4" },
  { source: "8", target: "12" },
  { source: "10", target: "11" },
  { source: "1", target: "9" },
];

export default function KnowledgeGraphPage() {
  return (
    <div className="pb-10">
      <PageHeader
        title="Knowledge Graph Explorer"
        description="Entity relationships across ownership, contracts, people, and risk signals — traced from source documents."
        actions={
          <>
            <Button variant="outline" size="sm">
              <Layers className="h-3.5 w-3.5" />
              Layers
            </Button>
            <Button variant="outline" size="sm">
              <Maximize2 className="h-3.5 w-3.5" />
              Expand
            </Button>
          </>
        }
      />

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-3 px-6">
        <Card className="xl:col-span-3">
          <CardHeader>
            <div>
              <CardTitle>Vantage Freight Ltd. — relationship graph</CardTitle>
              <CardDescription>13 entities · 13 traced relationships</CardDescription>
            </div>
            <div className="flex items-center gap-3">
              {categories.map((c) => (
                <span key={c.name} className="flex items-center gap-1.5 text-2xs text-ink-400">
                  <span className="h-1.5 w-1.5 rounded-full" style={{ background: c.color }} />
                  {c.name}
                </span>
              ))}
            </div>
          </CardHeader>
          <CardContent>
            <EChart
              height={480}
              option={{
                tooltip: { formatter: "{b}" },
                legend: { show: false },
                series: [
                  {
                    type: "graph",
                    layout: "force",
                    roam: true,
                    draggable: true,
                    categories,
                    data: nodes,
                    links,
                    force: { repulsion: 220, edgeLength: [60, 140], gravity: 0.12 },
                    label: {
                      show: true,
                      position: "right",
                      fontSize: 10,
                      color: CHART_COLORS.ink,
                    },
                    lineStyle: { color: "#33383F", curveness: 0.15, width: 1.2 },
                    itemStyle: { borderColor: "#0A0B0D", borderWidth: 2 },
                    emphasis: {
                      focus: "adjacency",
                      lineStyle: { width: 2.5 },
                      label: { fontWeight: 600 },
                    },
                  } as any,
                ],
              }}
            />
          </CardContent>
        </Card>

        <div className="space-y-3">
          <Card>
            <CardHeader>
              <CardTitle>Selected node</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <div>
                <div className="text-[13px] font-medium text-ink-100">
                  Model drift — pricing engine
                </div>
                <div className="text-2xs text-ink-600">Risk signal · SIG-4471</div>
              </div>
              <Badge variant="critical" dot>critical</Badge>
              <p className="text-2xs text-ink-400 leading-relaxed">
                Detected via automated model monitoring on Vantage Freight&apos;s
                dynamic pricing service. Directly linked to a sanctions-proximity
                signal through shared route-partner Bharat Agrotech.
              </p>
              <div className="hairline-top pt-3 space-y-2">
                <div className="flex justify-between text-2xs">
                  <span className="text-ink-600">First observed</span>
                  <span className="mono-data text-ink-100">2026-09-14</span>
                </div>
                <div className="flex justify-between text-2xs">
                  <span className="text-ink-600">Confidence</span>
                  <span className="mono-data text-ink-100">0.91</span>
                </div>
                <div className="flex justify-between text-2xs">
                  <span className="text-ink-600">Connected entities</span>
                  <span className="mono-data text-ink-100">4</span>
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Path finder</CardTitle>
              <CardDescription>Shortest link between two entities</CardDescription>
            </CardHeader>
            <CardContent className="space-y-2">
              <div className="panel-raised px-3 py-2 text-[13px] text-ink-100">Vantage Freight Ltd.</div>
              <div className="text-center text-ink-600 text-xs">↓ 3 hops</div>
              <div className="panel-raised px-3 py-2 text-[13px] text-ink-100">RBI</div>
              <Button variant="outline" size="sm" className="w-full mt-1">Trace another path</Button>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
