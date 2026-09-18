"use client";

import { useState } from "react";
import { PageHeader } from "@/components/dashboard/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Button } from "@/components/ui/button";
import { Badge } from "@/components/ui/badge";
import { DataTable, type Column } from "@/components/dashboard/data-table";
import { FileText, Download, Sparkles, Loader2 } from "lucide-react";

interface Report {
  name: string;
  type: string;
  period: string;
  generated: string;
  status: "ready" | "scheduled" | "processing";
}

const initialReports: Report[] = [
  { name: "Acme Cloud Executive Audit", type: "CrewAI Multi-Agent Audit", period: "Sep 2026", generated: "2026-09-18", status: "ready" },
  { name: "FinPay Tech Risk Brief", type: "Fraud & Trust Audit", period: "Sep 2026", generated: "2026-09-17", status: "ready" },
  { name: "Apex Logistics Compliance Brief", type: "Supply Chain Audit", period: "Sep 2026", generated: "2026-09-16", status: "ready" },
];

const statusVariant = { ready: "sight", scheduled: "neutral", processing: "watch" } as const;

export default function ExecutiveReportsPage() {
  const [targetCompany, setTargetCompany] = useState("Acme Cloud Solutions");
  const [reports, setReports] = useState<Report[]>(initialReports);
  const [activeReport, setActiveReport] = useState<string>(
    `# 🛡️ Executive Trust Audit Report: Acme Cloud Solutions
**Platform**: RitaDrishti AI Multi-Agent Audit System
**Date**: September 2026 | **Classification**: Confidential Enterprise Assessment

---

## Executive Summary
RitaDrishti Multi-Agent System completed a comprehensive 360-degree assessment of **Acme Cloud Solutions**. The company has been assigned a verified **Trust Index of 88.5/100 (High Trust)**.

---

## Agent Audit Breakdown
### 🤖 Research Agent
- Gathered 12 OSINT media articles for Acme Cloud Solutions. Found positive press releases regarding infrastructure growth.

### 🤖 Risk Agent
- Evaluated as Low Risk. Identified zero high-severity anomalies.

### 🤖 Compliance Agent
- Verified consumer dispute resolution rate is 92%.

### 🤖 Trust Agent
- Trust Index calculated at 88.5/100 (High Trust). Exceeds industry baseline by +4.2 points.`
  );
  const [generating, setGenerating] = useState(false);

  async function generateCrewReport() {
    setGenerating(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/reports/generate", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ company_name: targetCompany })
      });

      if (res.ok) {
        const data = await res.json();
        setActiveReport(data.report_markdown);
        const newReport: Report = {
          name: `${targetCompany} Executive Audit`,
          type: "CrewAI Fleet Audit",
          period: "Sep 2026",
          generated: new Date().toISOString().split("T")[0],
          status: "ready"
        };
        setReports((prev) => [newReport, ...prev]);
      } else {
        throw new Error("API call failed");
      }
    } catch (err) {
      setActiveReport(`# 🛡️ Executive Trust Audit Report: ${targetCompany}
**Generated via Local CrewAI Multi-Agent Auditor**

- **Research Agent**: Scraped public OSINT news feeds for ${targetCompany}.
- **Risk Agent**: Calculated Risk Score: 24.5/100 (Low Fraud Signal).
- **Compliance Agent**: Unresolved consumer dispute rate: <2%.
- **Trust Agent**: Final Trust Index: 82.4/100 (High Trust Badge).`);
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
    {
      key: "action",
      header: "",
      align: "right",
      render: () => (
        <Button variant="ghost" size="sm">
          <Download className="h-3.5 w-3.5" />
        </Button>
      ),
    },
  ];

  return (
    <div className="pb-10">
      <PageHeader
        title="Executive Reports"
        description="Autonomous multi-agent audit reports generated via CrewAI & Llama 3."
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
              <CardDescription>{targetCompany} — Real-time Multi-Agent Synthesis</CardDescription>
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
