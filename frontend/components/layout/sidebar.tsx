"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Gauge,
  Building2,
  ShieldCheck,
  AlertTriangle,
  Share2,
  Sparkles,
  FileBarChart2,
  Eye,
  Settings,
  LifeBuoy,
} from "lucide-react";
import { cn } from "@/lib/utils";

const NAV = [
  { href: "/", label: "Home Dashboard", icon: Gauge },
  { href: "/company-intelligence", label: "Company Intelligence", icon: Building2 },
  { href: "/trust-analytics", label: "Trust Analytics", icon: ShieldCheck },
  { href: "/risk-center", label: "Risk Center", icon: AlertTriangle },
  { href: "/knowledge-graph", label: "Knowledge Graph", icon: Share2 },
  { href: "/ai-copilot", label: "AI Copilot", icon: Sparkles },
  { href: "/executive-reports", label: "Executive Reports", icon: FileBarChart2 },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <aside className="hidden lg:flex w-[232px] shrink-0 flex-col bg-graphite-900 border-r border-line">
      <div className="flex items-center gap-2.5 h-14 px-4 border-b border-line">
        <div className="relative flex h-7 w-7 items-center justify-center rounded-md bg-signal-faint border border-signal-dim/40">
          <Eye className="h-3.5 w-3.5 text-signal" strokeWidth={2} />
        </div>
        <div className="leading-none">
          <div className="text-[13px] font-semibold tracking-tight text-ink-100">
            RitaDrishti
          </div>
          <div className="text-2xs text-ink-600 tracking-wide">
            Intelligence Platform
          </div>
        </div>
      </div>

      <nav className="flex-1 overflow-y-auto py-3 px-2.5 space-y-0.5">
        <div className="px-2 pb-1.5 pt-1 text-2xs font-medium text-ink-600 tracking-wide">
          Workspace
        </div>
        {NAV.map((item) => {
          const active = pathname === item.href;
          const Icon = item.icon;
          return (
            <Link
              key={item.href}
              href={item.href}
              className={cn(
                "group flex items-center gap-2.5 rounded-sm px-2.5 py-[7px] text-[13px] transition-colors",
                active
                  ? "bg-graphite-700 text-ink-100"
                  : "text-ink-400 hover:bg-graphite-800 hover:text-ink-100"
              )}
            >
              <Icon
                className={cn(
                  "h-4 w-4 shrink-0",
                  active ? "text-signal" : "text-ink-600 group-hover:text-ink-400"
                )}
                strokeWidth={1.75}
              />
              <span className="truncate">{item.label}</span>
              {active && (
                <span className="ml-auto h-1.5 w-1.5 rounded-full bg-signal" />
              )}
            </Link>
          );
        })}
      </nav>

      <div className="border-t border-line p-2.5 space-y-0.5">
        <button className="flex w-full items-center gap-2.5 rounded-sm px-2.5 py-[7px] text-[13px] text-ink-400 hover:bg-graphite-800 hover:text-ink-100 transition-colors">
          <Settings className="h-4 w-4 text-ink-600" strokeWidth={1.75} />
          Platform settings
        </button>
        <button className="flex w-full items-center gap-2.5 rounded-sm px-2.5 py-[7px] text-[13px] text-ink-400 hover:bg-graphite-800 hover:text-ink-100 transition-colors">
          <LifeBuoy className="h-4 w-4 text-ink-600" strokeWidth={1.75} />
          Support
        </button>
      </div>
    </aside>
  );
}
