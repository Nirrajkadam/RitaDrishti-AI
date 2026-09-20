"use client";

import { useState } from "react";
import { Building2, Plus, Loader2, AlertCircle } from "lucide-react";
import { Dialog, DialogContent, DialogHeader, DialogTitle, DialogDescription } from "@/components/ui/dialog";
import { Button } from "@/components/ui/button";
import { apiFetch } from "@/lib/api";

interface CreateCompanyModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCompanyCreated: (company: any) => void;
}

export function CreateCompanyModal({ isOpen, onClose, onCompanyCreated }: CreateCompanyModalProps) {
  const [loading, setLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);

  const [name, setName] = useState("");
  const [domain, setDomain] = useState("");
  const [industry, setIndustry] = useState("Fintech");
  const [description, setDescription] = useState("");

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    if (!name.trim() || !domain.trim()) {
      setErrorMessage("Company name and domain are required.");
      return;
    }

    setLoading(true);
    setErrorMessage(null);

    try {
      const newCompany: any = await apiFetch("/api/v1/companies/", {
        method: "POST",
        body: JSON.stringify({
          name: name.trim(),
          domain: domain.trim().toLowerCase(),
          industry: industry.trim() || "Fintech",
          description: description.trim() || undefined,
        }),
      });

      onCompanyCreated(newCompany);
      setName("");
      setDomain("");
      setDescription("");
      onClose();
    } catch (err: any) {
      setErrorMessage(err.message || "Failed to register company.");
    } finally {
      setLoading(false);
    }
  }

  return (
    <Dialog open={isOpen} onOpenChange={(open) => !open && onClose()}>
      <DialogContent className="sm:max-w-[450px] border-slate-800 bg-slate-950 text-white">
        <DialogHeader>
          <DialogTitle className="flex items-center gap-2 text-xl font-bold text-sky-400">
            <Building2 className="h-6 w-6 text-sky-400" />
            Register Target Company
          </DialogTitle>
          <DialogDescription className="text-slate-400">
            Add a new enterprise domain to the database for trust intelligence auditing.
          </DialogDescription>
        </DialogHeader>

        {errorMessage && (
          <div className="flex items-start gap-2 p-3 rounded bg-red-950/60 border border-red-800 text-red-300 text-sm">
            <AlertCircle className="h-5 w-5 shrink-0 text-red-400 mt-0.5" />
            <span>{errorMessage}</span>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4 pt-2">
          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1">Company Name</label>
            <input
              type="text"
              required
              value={name}
              onChange={(e) => setName(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-800 text-sm focus:border-sky-500 focus:outline-none"
              placeholder="Acme Payments Corp"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1">Domain Name</label>
            <input
              type="text"
              required
              value={domain}
              onChange={(e) => setDomain(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-800 text-sm focus:border-sky-500 focus:outline-none"
              placeholder="acmepayments.io"
            />
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1">Industry Sector</label>
            <select
              value={industry}
              onChange={(e) => setIndustry(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-800 text-sm focus:border-sky-500 focus:outline-none"
            >
              <option value="Fintech">Fintech & Payments</option>
              <option value="Cloud SaaS">Cloud SaaS & AI</option>
              <option value="Ecommerce">Ecommerce & Retail</option>
              <option value="Healthcare">Healthcare & Biotech</option>
              <option value="Cybersecurity">Cybersecurity & Defense</option>
            </select>
          </div>

          <div>
            <label className="block text-xs font-semibold text-slate-400 mb-1">Description (Optional)</label>
            <textarea
              value={description}
              onChange={(e) => setDescription(e.target.value)}
              className="w-full px-3 py-2 rounded bg-slate-900 border border-slate-800 text-sm focus:border-sky-500 focus:outline-none h-20"
              placeholder="Enterprise payment processing provider."
            />
          </div>

          <Button type="submit" disabled={loading} className="w-full bg-sky-600 hover:bg-sky-500 text-white font-semibold">
            {loading ? <Loader2 className="h-4 w-4 animate-spin mr-2" /> : <Plus className="h-4 w-4 mr-2" />}
            Register Company Domain
          </Button>
        </form>
      </DialogContent>
    </Dialog>
  );
}
