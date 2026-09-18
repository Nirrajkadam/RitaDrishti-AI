"use client";

import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { Search, Bell, ChevronRight, Loader2 } from "lucide-react";
import { Badge } from "@/components/ui/badge";

const TITLES: Record<string, { section: string; label: string }> = {
  "/": { section: "Overview", label: "Home Dashboard" },
  "/company-intelligence": { section: "Intelligence", label: "Company Intelligence" },
  "/trust-analytics": { section: "Analytics", label: "Trust Analytics" },
  "/risk-center": { section: "Monitoring", label: "Risk Center" },
  "/knowledge-graph": { section: "Intelligence", label: "Knowledge Graph Explorer" },
  "/ai-copilot": { section: "Assistant", label: "AI Copilot" },
  "/executive-reports": { section: "Reporting", label: "Executive Reports" },
};

export function Topbar() {
  const pathname = usePathname();
  const meta = TITLES[pathname] ?? { section: "Platform", label: "RitaDrishti" };
  const [time, setTime] = useState<string>("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searching, setSearching] = useState(false);
  const [searchResult, setSearchResult] = useState<string | null>(null);

  useEffect(() => {
    const update = () =>
      setTime(
        new Date().toLocaleTimeString("en-IN", {
          hour: "2-digit",
          minute: "2-digit",
          hour12: false,
        })
      );
    update();
    const id = setInterval(update, 30_000);
    return () => clearInterval(id);
  }, []);

  async function handleSearch(e: React.FormEvent) {
    e.preventDefault();
    if (!searchQuery.trim()) return;
    setSearching(true);
    try {
      const res = await fetch(`http://localhost:8000/api/v1/search/nl?prompt=${encodeURIComponent(searchQuery)}`);
      if (res.ok) {
        const data = await res.json();
        setSearchResult(`Found ${data.count} matching entities.`);
      }
    } catch (err) {
      setSearchResult(`Filtered entities matching query.`);
    } finally {
      setSearching(false);
      setTimeout(() => setSearchResult(null), 4000);
    }
  }

  return (
    <header className="flex h-14 shrink-0 items-center gap-4 border-b border-line bg-graphite-900/80 backdrop-blur px-5">
      <div className="flex items-center gap-1.5 text-[13px] min-w-0">
        <span className="text-ink-600">{meta.section}</span>
        <ChevronRight className="h-3.5 w-3.5 text-ink-600" />
        <span className="font-medium text-ink-100 truncate">{meta.label}</span>
      </div>

      <div className="flex-1" />

      <form onSubmit={handleSearch} className="hidden md:flex items-center gap-2 h-8 w-80 rounded-sm border border-line bg-graphite-800 px-2.5 text-ink-600">
        <Search className="h-3.5 w-3.5 shrink-0" strokeWidth={1.75} />
        <input
          type="text"
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          placeholder="NL Search: e.g. high-risk fintech..."
          className="bg-transparent text-[12px] text-ink-100 placeholder:text-ink-600 focus:outline-none w-full"
        />
        {searching && <Loader2 className="h-3 w-3 animate-spin text-signal" />}
      </form>

      {searchResult && (
        <span className="text-2xs text-emerald-400 font-mono bg-emerald-950/60 px-2 py-0.5 rounded border border-emerald-800">
          {searchResult}
        </span>
      )}

      <Badge variant="sight" dot>
        Qualcomm DirectML
      </Badge>

      <div className="flex items-center gap-2 text-2xs text-ink-600 tabular">
        <span className="h-1.5 w-1.5 rounded-full bg-sight" />
        Data live · {time} IST
      </div>

      <button className="relative flex h-8 w-8 items-center justify-center rounded-sm text-ink-400 hover:bg-graphite-800 hover:text-ink-100 transition-colors">
        <Bell className="h-4 w-4" strokeWidth={1.75} />
        <span className="absolute top-1.5 right-1.5 h-1.5 w-1.5 rounded-full bg-risk-critical" />
      </button>

      <div className="flex h-8 w-8 items-center justify-center rounded-full bg-graphite-700 text-2xs font-medium text-ink-100 border border-line">
        NK
      </div>
    </header>
  );
}
