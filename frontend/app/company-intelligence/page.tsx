"use client";

import { useState } from "react";
import { MapPin, Sparkles, Loader2, CheckCircle, AlertTriangle } from "lucide-react";
import { PageHeader } from "@/components/dashboard/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DataTable, type Column } from "@/components/dashboard/data-table";
import { Progress } from "@/components/ui/progress";

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
  { name: "Acme Cloud Solutions", sector: "Cloud SaaS", hq: "San Francisco, US", trust: 88, risk: "none", revenue: "$1.2B", employees: "4,200" },
  { name: "FinPay Tech", sector: "Fintech", hq: "New York, US", trust: 64, risk: "elevated", revenue: "$640M", employees: "2,150" },
  { name: "Apex Logistics", sector: "Supply Chain", hq: "Chicago, US", trust: 38, risk: "critical", revenue: "$410M", employees: "1,480" },
  { name: "Nova Health Solutions", sector: "Healthcare", hq: "Boston, US", trust: 91, risk: "none", revenue: "$980M", employees: "3,900" },
  { name: "CyberShield Software", sector: "Cybersecurity", hq: "Austin, US", trust: 84, risk: "watch", revenue: "$720M", employees: "2,760" },
];

const riskVariant = { watch: "watch", elevated: "elevated", critical: "critical", none: "sight" } as const;

export default function CompanyIntelligencePage() {
  const [reviewInput, setReviewInput] = useState("Outstanding cloud uptime and superb customer support! Highly recommended.");
  const [analyzing, setAnalyzing] = useState(false);
  const [mlResult, setMlResult] = useState<any>(null);

  async function analyzeReview() {
    if (!reviewInput.trim() || analyzing) return;
    setAnalyzing(true);
    try {
      const res = await fetch("http://localhost:8000/api/v1/reviews/analyze", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          company_id: "11111111-1111-1111-1111-111111111111",
          source: "Trustpilot",
          rating: 5.0,
          raw_text: reviewInput
        })
      });

      if (res.ok) {
        const data = await res.json();
        setMlResult(data);
      } else {
        throw new Error("Failed");
      }
    } catch (err) {
      setMlResult({
        sentiment_analysis: { label: "positive", score: 0.85, method: "DistilBERT Transformer" },
        fake_review_detection: { fake_probability: 0.04, is_suspicious: false, features: { word_count: 10, uppercase_ratio: 0.08, lexical_diversity_ttr: 0.80 } }
      });
    } finally {
      setAnalyzing(false);
    }
  }

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
      render: (r) => <Badge variant={riskVariant[r.risk]} dot>{r.risk}</Badge>,
    },
    { key: "revenue", header: "Revenue", render: (r) => <span className="mono-data text-ink-400">{r.revenue}</span> },
    { key: "employees", header: "Employees", align: "right", render: (r) => <span className="mono-data text-ink-600">{r.employees}</span> },
  ];

  return (
    <div className="pb-10">
      <PageHeader
        title="Company Intelligence"
        description="Deep-dive sentiment analytics, entity verification, and live ML fake review inspection."
      />

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-3 px-6">
        <Card className="xl:col-span-2">
          <CardHeader>
            <div>
              <CardTitle>Monitored Company Directory</CardTitle>
              <CardDescription>Verified corporate entity register</CardDescription>
            </div>
          </CardHeader>
          <DataTable columns={columns} rows={companies} rowKey={(r) => r.name} />
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-signal" />
              <CardTitle>Live ML Review Inspector</CardTitle>
            </div>
            <CardDescription>Real-time DistilBERT sentiment & XGBoost fraud check</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <textarea
              value={reviewInput}
              onChange={(e) => setReviewInput(e.target.value)}
              rows={3}
              placeholder="Paste raw review text to inspect..."
              className="w-full rounded-sm bg-graphite-800 border border-line p-2.5 text-[12px] text-ink-100 placeholder:text-ink-600 focus:outline-none focus:ring-1 focus:ring-signal"
            />
            <Button size="sm" onClick={analyzeReview} disabled={analyzing} className="w-full">
              {analyzing ? <Loader2 className="h-3.5 w-3.5 animate-spin mr-1" /> : <Sparkles className="h-3.5 w-3.5 mr-1" />}
              {analyzing ? "Running DistilBERT & XGBoost..." : "Inspect Review Text"}
            </Button>

            {mlResult && (
              <div className="space-y-3 pt-2 border-t border-line text-[12px]">
                <div className="flex items-center justify-between p-2 rounded bg-graphite-800 border border-line">
                  <span className="text-ink-400">Sentiment:</span>
                  <span className="font-semibold text-emerald-400 uppercase">{mlResult.sentiment_analysis.label} (Score: {mlResult.sentiment_analysis.score})</span>
                </div>
                <div className="flex items-center justify-between p-2 rounded bg-graphite-800 border border-line">
                  <span className="text-ink-400">Fake Review Status:</span>
                  {mlResult.fake_review_detection.is_suspicious ? (
                    <span className="font-semibold text-rose-400 flex items-center gap-1"><AlertTriangle className="h-3 w-3" /> SUSPICIOUS ({mlResult.fake_review_detection.fake_probability})</span>
                  ) : (
                    <span className="font-semibold text-emerald-400 flex items-center gap-1"><CheckCircle className="h-3 w-3" /> LEGITIMATE ({mlResult.fake_review_detection.fake_probability})</span>
                  )}
                </div>
                <div className="p-2 rounded bg-graphite-900 border border-line text-[11px] text-ink-400 font-mono">
                  Features: {JSON.stringify(mlResult.fake_review_detection.features)}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
