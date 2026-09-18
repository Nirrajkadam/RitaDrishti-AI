"use client";

import { usePathname } from "next/navigation";
import { useEffect, useState } from "react";
import { Search, Bell, ChevronRight } from "lucide-react";
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

  return (
    <header className="flex h-14 shrink-0 items-center gap-4 border-b border-line bg-graphite-900/80 backdrop-blur px-5">
      <div className="flex items-center gap-1.5 text-[13px] min-w-0">
        <span className="text-ink-600">{meta.section}</span>
        <ChevronRight className="h-3.5 w-3.5 text-ink-600" />
        <span className="font-medium text-ink-100 truncate">{meta.label}</span>
      </div>

      <div className="flex-1" />

      <div className="hidden md:flex items-center gap-2 h-8 w-72 rounded-sm border border-line bg-graphite-800 px-2.5 text-ink-600">
        <Search className="h-3.5 w-3.5" strokeWidth={1.75} />
        <span className="text-[13px]">Search entities, models, reports…</span>
        <kbd className="ml-auto text-2xs border border-line rounded-sm px-1 py-0.5 text-ink-600">
          ⌘K
        </kbd>
      </div>

      <Badge variant="sight" dot>
        Production
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
        NP
      </div>
    </header>
  );
}
