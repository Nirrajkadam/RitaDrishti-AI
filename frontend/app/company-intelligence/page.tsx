"use client";

import { useState, useEffect } from "react";
import { MapPin, Sparkles, Loader2, CheckCircle, AlertTriangle, AlertCircle } from "lucide-react";
import { PageHeader } from "@/components/dashboard/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DataTable, type Column } from "@/components/dashboard/data-table";
import { Progress } from "@/components/ui/progress";
import { apiFetch, setAuthToken, getAuthToken } from "@/lib/api";

interface CompanyResponse {
  company_id: string;
  name: string;
  domain: string;
  industry: string;
  description?: string;
  verified_status: boolean;
  country_code: string;
  created_at: string;
}

export default function CompanyIntelligencePage() {
  const [companies, setCompanies] = useState<CompanyResponse[]>([]);
  const [selectedCompanyId, setSelectedCompanyId] = useState<string>("");
  const [reviewInput, setReviewInput] = useState("BEST PRODUCT EVER!!! Contact john.doe@example.com for 20% discount. MUST BUY HIGHLY RECOMMENDED 100% FIVE STARS!!");
  const [analyzing, setAnalyzing] = useState(false);
  const [mlResult, setMlResult] = useState<any>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [authenticatedUser, setAuthenticatedUser] = useState<string | null>(null);

  // Authenticate & load company directory on mount
  useEffect(() => {
    async function initSessionAndCompanies() {
      try {
        if (!getAuthToken()) {
          // Register demo analyst account
          try {
            const regRes: any = await apiFetch("/api/v1/auth/register", {
              method: "POST",
              body: JSON.stringify({
                email: `analyst_${Date.now()}@ritadrishti.ai`,
                username: `analyst_${Date.now()}`,
                password: "SecurePassword123!",
                full_name: "Auditor Analyst"
              })
            });
            setAuthenticatedUser(regRes.username);
          } catch (regErr) {
            // Fallback login if already registered
          }

          const loginRes: any = await apiFetch("/api/v1/auth/login", {
            method: "POST",
            body: JSON.stringify({
              username: "testuser",
              password: "TestPassword123!"
            })
          }).catch(() => null);

          if (loginRes?.access_token) {
            setAuthToken(loginRes.access_token);
            setAuthenticatedUser(loginRes.username);
          }
        }

        // Fetch Companies from backend DB
        const companyList = await apiFetch<CompanyResponse[]>("/api/v1/companies/");
        if (companyList && companyList.length > 0) {
          setCompanies(companyList);
          setSelectedCompanyId(companyList[0].company_id);
        } else {
          // Create initial company record in DB
          const newCompany = await apiFetch<CompanyResponse>("/api/v1/companies/", {
            method: "POST",
            body: JSON.stringify({
              name: "Acme Cloud Solutions",
              domain: `acmecloud_${Date.now()}.io`,
              industry: "Cloud SaaS",
              description: "Enterprise SaaS provider offering cloud infrastructure & AI middleware."
            })
          });
          setCompanies([newCompany]);
          setSelectedCompanyId(newCompany.company_id);
        }
      } catch (err: any) {
        setErrorMessage(err.message || "Session initialization failed.");
      }
    }

    initSessionAndCompanies();
  }, []);

  async function analyzeReview() {
    if (!reviewInput.trim() || analyzing || !selectedCompanyId) return;
    setAnalyzing(true);
    setErrorMessage(null);
    setMlResult(null);

    try {
      const data = await apiFetch<any>("/api/v1/reviews/analyze", {
        method: "POST",
        body: JSON.stringify({
          company_id: selectedCompanyId,
          source: "Trustpilot",
          rating: 5.0,
          raw_text: reviewInput,
          reviewer_name: "Verified Auditor"
        })
      });

      setMlResult(data);
    } catch (err: any) {
      setErrorMessage(err.message || "ML Review Analysis Request Failed.");
    } finally {
      setAnalyzing(false);
    }
  }

  const columns: Column<CompanyResponse>[] = [
    {
      key: "name",
      header: "Entity & Domain",
      render: (r) => (
        <div>
          <div className="font-medium text-ink-100">{r.name}</div>
          <div className="text-2xs text-ink-600 flex items-center gap-1 mt-0.5">
            <MapPin className="h-2.5 w-2.5" /> {r.domain} ({r.country_code})
          </div>
        </div>
      ),
    },
    { key: "industry", header: "Industry", render: (r) => <span className="text-ink-400">{r.industry}</span> },
    {
      key: "verified_status",
      header: "Verification",
      render: (r) => <Badge variant={r.verified_status ? "sight" : "watch"} dot>{r.verified_status ? "VERIFIED" : "AUDITING"}</Badge>,
    },
    {
      key: "actions",
      header: "Action",
      align: "right",
      render: (r) => (
        <Button
          size="sm"
          variant={selectedCompanyId === r.company_id ? "default" : "outline"}
          onClick={() => setSelectedCompanyId(r.company_id)}
        >
          {selectedCompanyId === r.company_id ? "Selected Target" : "Select Target"}
        </Button>
      ),
    },
  ];

  return (
    <div className="pb-10">
      <PageHeader
        title="Company Intelligence & ML Review Inspector"
        description="Authenticated vertical workflow: PII sanitization, joblib model inference, and atomic DB persistence."
      />

      {authenticatedUser && (
        <div className="mx-6 mb-3 p-2.5 rounded bg-graphite-800 border border-line text-[12px] flex items-center justify-between">
          <span className="text-ink-400">Authenticated Session: <strong className="text-emerald-400">{authenticatedUser}</strong></span>
          <Badge variant="sight">Bearer JWT Active</Badge>
        </div>
      )}

      {errorMessage && (
        <div className="mx-6 mb-3 p-3 rounded bg-rose-950/60 border border-rose-800/80 text-[12px] text-rose-300 flex items-center gap-2">
          <AlertCircle className="h-4 w-4 text-rose-400 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-3 px-6">
        <Card className="xl:col-span-2">
          <CardHeader>
            <div>
              <CardTitle>Monitored Corporate Directory</CardTitle>
              <CardDescription>Real DB records fetched from /api/v1/companies/</CardDescription>
            </div>
          </CardHeader>
          <DataTable columns={columns} rows={companies} rowKey={(r) => r.company_id} />
        </Card>

        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Sparkles className="h-4 w-4 text-signal" />
              <CardTitle>Live ML Review Inspector</CardTitle>
            </div>
            <CardDescription>Submits review to /api/v1/reviews/analyze with PII redaction & ML inference</CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <textarea
              value={reviewInput}
              onChange={(e) => setReviewInput(e.target.value)}
              rows={4}
              placeholder="Paste raw review text to inspect..."
              className="w-full rounded-sm bg-graphite-800 border border-line p-2.5 text-[12px] text-ink-100 placeholder:text-ink-600 focus:outline-none focus:ring-1 focus:ring-signal"
            />
            <Button size="sm" onClick={analyzeReview} disabled={analyzing || !selectedCompanyId} className="w-full">
              {analyzing ? <Loader2 className="h-3.5 w-3.5 animate-spin mr-1" /> : <Sparkles className="h-3.5 w-3.5 mr-1" />}
              {analyzing ? "Sanitizing PII & Running ML Model..." : "Analyze & Persist Review"}
            </Button>

            {mlResult && (
              <div className="space-y-3 pt-2 border-t border-line text-[12px]">
                <div className="p-2 rounded bg-graphite-900 border border-line">
                  <div className="text-2xs text-ink-500 font-mono mb-1">PII SANITIZED TEXT (PERSISTED):</div>
                  <div className="text-ink-200 text-[11px] font-mono">{mlResult.review?.cleaned_text}</div>
                </div>

                <div className="flex items-center justify-between p-2 rounded bg-graphite-800 border border-line">
                  <span className="text-ink-400">Sentiment Score:</span>
                  <span className="font-semibold text-emerald-400 uppercase">
                    {mlResult.analysis?.sentiment_label} ({mlResult.analysis?.sentiment_score})
                  </span>
                </div>

                <div className="flex items-center justify-between p-2 rounded bg-graphite-800 border border-line">
                  <span className="text-ink-400">ML Fake Probability:</span>
                  {mlResult.analysis?.is_suspicious ? (
                    <span className="font-semibold text-rose-400 flex items-center gap-1">
                      <AlertTriangle className="h-3 w-3" /> SUSPICIOUS ({(mlResult.analysis?.fake_probability * 100).toFixed(1)}%)
                    </span>
                  ) : (
                    <span className="font-semibold text-emerald-400 flex items-center gap-1">
                      <CheckCircle className="h-3 w-3" /> LEGITIMATE ({(mlResult.analysis?.fake_probability * 100).toFixed(1)}%)
                    </span>
                  )}
                </div>

                <div className="p-2 rounded bg-graphite-900 border border-line text-[11px] text-ink-400 font-mono overflow-x-auto">
                  Model: {mlResult.analysis?.model_version}<br/>
                  Features: {JSON.stringify(mlResult.analysis?.feature_metrics)}
                </div>
              </div>
            )}
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
