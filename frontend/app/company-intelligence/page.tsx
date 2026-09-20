"use client";

import { useState, useEffect } from "react";
import { MapPin, Sparkles, Loader2, CheckCircle, AlertTriangle, AlertCircle, LogIn, LogOut, Plus, Building2 } from "lucide-react";
import { PageHeader } from "@/components/dashboard/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { DataTable, type Column } from "@/components/dashboard/data-table";
import { apiFetch, setAuthToken, getAuthToken, removeAuthToken } from "@/lib/api";
import { AuthModal } from "@/components/auth-modal";
import { CreateCompanyModal } from "@/components/create-company-modal";

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

  // Modals state
  const [isAuthModalOpen, setIsAuthModalOpen] = useState(false);
  const [isCreateCompanyModalOpen, setIsCreateCompanyModalOpen] = useState(false);

  // Load companies from backend DB
  async function fetchCompanies() {
    try {
      const companyList = await apiFetch<CompanyResponse[]>("/api/v1/companies/");
      if (companyList && companyList.length > 0) {
        setCompanies(companyList);
        if (!selectedCompanyId) {
          setSelectedCompanyId(companyList[0].company_id);
        }
      } else {
        setCompanies([]);
        setSelectedCompanyId("");
      }
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to load company directory.");
    }
  }

  // Check auth session on mount
  useEffect(() => {
    async function checkSession() {
      const token = getAuthToken();
      if (!token) {
        setAuthenticatedUser(null);
        setIsAuthModalOpen(true);
        return;
      }

      try {
        const user: any = await apiFetch("/api/v1/auth/me");
        setAuthenticatedUser(user.username || user.email || "Authenticated Auditor");
        await fetchCompanies();
      } catch (err) {
        removeAuthToken();
        setAuthenticatedUser(null);
        setIsAuthModalOpen(true);
      }
    }

    checkSession();

    function handleUnauthorized() {
      setAuthenticatedUser(null);
      setIsAuthModalOpen(true);
    }

    if (typeof window !== "undefined") {
      window.addEventListener("ritadrishti_unauthorized", handleUnauthorized);
      return () => window.removeEventListener("ritadrishti_unauthorized", handleUnauthorized);
    }
  }, []);

  function handleLogout() {
    removeAuthToken();
    setAuthenticatedUser(null);
    setCompanies([]);
    setSelectedCompanyId("");
    setMlResult(null);
    setIsAuthModalOpen(true);
  }

  function handleAuthenticated(username: string) {
    setAuthenticatedUser(username);
    setIsAuthModalOpen(false);
    fetchCompanies();
  }

  function handleCompanyCreated(newCompany: CompanyResponse) {
    setCompanies((prev) => [newCompany, ...prev]);
    setSelectedCompanyId(newCompany.company_id);
  }

  async function analyzeReview() {
    if (!reviewInput.trim() || analyzing) return;
    if (!authenticatedUser) {
      setIsAuthModalOpen(true);
      return;
    }
    if (!selectedCompanyId) {
      setErrorMessage("Please register or select a target company domain first.");
      return;
    }

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
          reviewer_name: authenticatedUser
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

      {/* Explicit Auth Status Banner */}
      <div className="mx-6 mb-3 p-3 rounded bg-slate-900 border border-slate-800 text-[12px] flex items-center justify-between">
        <div className="flex items-center gap-2">
          {authenticatedUser ? (
            <>
              <Badge variant="sight">Authenticated Auditor</Badge>
              <span className="text-slate-300">
                Logged in as: <strong className="text-emerald-400">{authenticatedUser}</strong>
              </span>
            </>
          ) : (
            <>
              <Badge variant="watch">Unauthenticated</Badge>
              <span className="text-amber-300">Please sign in or register an account to access company auditing workflows.</span>
            </>
          )}
        </div>

        <div className="flex items-center gap-2">
          {authenticatedUser ? (
            <>
              <Button size="sm" variant="outline" onClick={() => setIsCreateCompanyModalOpen(true)}>
                <Plus className="h-3.5 w-3.5 mr-1" /> Register New Company
              </Button>
              <Button size="sm" variant="destructive" onClick={handleLogout}>
                <LogOut className="h-3.5 w-3.5 mr-1" /> Log Out
              </Button>
            </>
          ) : (
            <Button size="sm" className="bg-sky-600 hover:bg-sky-500 text-white" onClick={() => setIsAuthModalOpen(true)}>
              <LogIn className="h-3.5 w-3.5 mr-1" /> Sign In / Register
            </Button>
          )}
        </div>
      </div>

      {errorMessage && (
        <div className="mx-6 mb-3 p-3 rounded bg-rose-950/60 border border-rose-800/80 text-[12px] text-rose-300 flex items-center gap-2">
          <AlertCircle className="h-4 w-4 text-rose-400 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      <div className="grid grid-cols-1 xl:grid-cols-3 gap-3 px-6">
        <Card className="xl:col-span-2">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle>Monitored Corporate Directory</CardTitle>
                <CardDescription>Real DB records fetched from /api/v1/companies/</CardDescription>
              </div>
              {authenticatedUser && (
                <Button size="sm" variant="outline" onClick={() => setIsCreateCompanyModalOpen(true)}>
                  <Building2 className="h-3.5 w-3.5 mr-1" /> Add Company
                </Button>
              )}
            </div>
          </CardHeader>

          {companies.length > 0 ? (
            <DataTable columns={columns} rows={companies} rowKey={(r) => r.company_id} />
          ) : (
            <CardContent className="py-12 text-center text-slate-400 text-sm">
              <Building2 className="h-10 w-10 text-slate-600 mx-auto mb-3" />
              <p>No target companies currently registered in database.</p>
              {authenticatedUser && (
                <Button size="sm" className="mt-3 bg-sky-600 hover:bg-sky-500 text-white" onClick={() => setIsCreateCompanyModalOpen(true)}>
                  <Plus className="h-3.5 w-3.5 mr-1" /> Create First Target Company
                </Button>
              )}
            </CardContent>
          )}
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
            <Button size="sm" onClick={analyzeReview} disabled={analyzing || !selectedCompanyId || !authenticatedUser} className="w-full">
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

      {/* Modals */}
      <AuthModal
        isOpen={isAuthModalOpen}
        onClose={() => setIsAuthModalOpen(false)}
        onAuthenticated={handleAuthenticated}
      />

      <CreateCompanyModal
        isOpen={isCreateCompanyModalOpen}
        onClose={() => setIsCreateCompanyModalOpen(false)}
        onCompanyCreated={handleCompanyCreated}
      />
    </div>
  );
}
