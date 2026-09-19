"use client";

import { useState } from "react";
import { PageHeader } from "@/components/dashboard/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { DataTable, type Column } from "@/components/dashboard/data-table";
import { FileText, Download, Sparkles, Loader2, AlertCircle } from "lucide-react";
import { apiFetch } from "@/lib/api";

interface Report {
  name: string;
  type: string;
  period: string;
  generated: string;
  status: "ready" | "scheduled" | "processing";
}

const initialReports: Report[] = [];

const statusVariant = { ready: "sight", scheduled: "neutral", processing: "watch" } as const;

export default function ExecutiveReportsPage() {
  const [targetCompany, setTargetCompany] = useState("Acme Cloud Solutions");
  const [reports, setReports] = useState<Report[]>(initialReports);
  const [activeReport, setActiveReport] = useState<string>(
    `# Executive Report Viewer\n\nSelect a target company and click **Run CrewAI Audit** to generate a multi-agent report. Note: Optional subsystems require \`ENABLE_CREWAI=true\` in backend configuration.`
  );
  const [generating, setGenerating] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  async function generateCrewReport() {
    setGenerating(true);
    setErrorMessage(null);

    try {
      const data: any = await apiFetch("/api/v1/reports/generate", {
        method: "POST",
        body: JSON.stringify({ company_name: targetCompany })
      });

      setActiveReport(data.report_markdown);
      const newReport: Report = {
        name: `${targetCompany} Executive Audit`,
        type: "CrewAI Fleet Audit",
        period: "Sep 2026",
        generated: new Date().toISOString().split("T")[0],
        status: "ready"
      };
      setReports((prev) => [newReport, ...prev]);
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to generate executive report.");
      setActiveReport(`⚠️ **Report Generation Status**: ${err.message || "Request failed."}`);
    } finally {
      setGenerating(false);
    }
  }

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
  ];

  return (
    <div className="pb-10">
      <PageHeader
        title="Executive Reports"
        description="Autonomous multi-agent audit reports generated via CrewAI."
        actions={
          <div className="flex items-center gap-2">
            <select
              value={targetCompany}
              onChange={(e) => setTargetCompany(e.target.value)}
              className="h-8 rounded-sm bg-graphite-800 border border-line px-2 text-2xs text-ink-100 focus:outline-none"
            >
              <option value="Acme Cloud Solutions">Acme Cloud Solutions</option>
              <option value="FinPay Tech">FinPay Tech</option>
              <option value="Apex Logistics">Apex Logistics</option>
            </select>
            <Button size="sm" onClick={generateCrewReport} disabled={generating}>
              {generating ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Sparkles className="h-3.5 w-3.5" />}
              {generating ? "Running Agents..." : "Run CrewAI Audit"}
            </Button>
          </div>
        }
      />

      {errorMessage && (
        <div className="mx-6 mb-3 p-3 rounded bg-rose-950/60 border border-rose-800/80 text-[12px] text-rose-300 flex items-center gap-2">
          <AlertCircle className="h-4 w-4 text-rose-400 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-3 px-6">
        <Card className="xl:col-span-1">
          <CardHeader>
            <div>
              <CardTitle>Generated Audit Library</CardTitle>
              <CardDescription>Multi-agent reports history</CardDescription>
            </div>
          </CardHeader>
          <DataTable columns={columns} rows={reports} rowKey={(r, i) => r.name + i} />
        </Card>

        <Card className="xl:col-span-2">
          <CardHeader className="flex flex-row items-center justify-between">
            <div>
              <CardTitle>Live CrewAI Report Viewer</CardTitle>
              <CardDescription>{targetCompany} — Multi-Agent Synthesis</CardDescription>
            </div>
            <Button variant="outline" size="sm">
              <Download className="h-3.5 w-3.5 mr-1" />
              Download Markdown
            </Button>
          </CardHeader>
          <CardContent>
            {generating ? (
              <div className="flex flex-col items-center justify-center py-16 text-ink-500 gap-3">
                <Loader2 className="h-8 w-8 animate-spin text-signal" />
                <p className="text-xs">Research, Risk, Compliance & Trust Agents compiling report...</p>
              </div>
            ) : (
              <div className="p-4 rounded-md bg-graphite-900 border border-line font-mono text-[12px] leading-relaxed text-ink-200 whitespace-pre-wrap overflow-y-auto max-h-[500px]">
                {activeReport}
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
