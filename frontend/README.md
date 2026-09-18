# RitaDrishti AI — Intelligence Platform UI

A Palantir/Foundry-inspired dark enterprise UI for an AI trust, risk, and
company-intelligence platform. Built with Next.js 14 (App Router),
Tailwind CSS, shadcn/ui-style primitives, and Apache ECharts.

## Getting started

```bash
npm install
npm run dev
```

Open http://localhost:3000.

> This was authored by hand (not scaffolded via `create-next-app` or the
> shadcn CLI) so every file is included below — running `npm install` will
> pull the listed dependencies, no `npx shadcn init` needed. The UI
> primitives in `components/ui/` already follow shadcn's file conventions,
> so the shadcn CLI can still be used later to add more components.

## Pages

| Route                   | Page                        |
|--------------------------|-----------------------------|
| `/`                      | Home Dashboard              |
| `/company-intelligence`  | Company Intelligence        |
| `/trust-analytics`       | Trust Analytics             |
| `/risk-center`           | Risk Center                 |
| `/knowledge-graph`       | Knowledge Graph Explorer    |
| `/ai-copilot`            | AI Copilot                  |
| `/executive-reports`     | Executive Reports           |

## Design system

- **Color** — graphite/void surfaces (`#0A0B0D` → `#2B3036`) with a single
  cool "signal" accent (`#6E6BFF`) for AI/intelligence affordances, a
  teal "sight" accent (`#35C7B5`) for trust/positive states, and a
  three-step amber → ember → crimson scale for risk severity.
- **Type** — Manrope for UI and headings; IBM Plex Mono reserved for
  metrics, IDs, and timestamps (`.mono-data` / `.tabular` utilities),
  never for general labels.
- **Layout** — fixed 232px icon+label sidebar, 56px topbar with global
  search, live data indicator, and breadcrumb; content in a responsive
  card grid with 1px hairline borders and 4–6px radii (not the generic
  soft-shadow rounded-card look).
- **Charts** — all ECharts instances share a single theme (`components/
  charts/echart.tsx`) so gridlines, tooltips, and the color palette stay
  consistent across line, bar, pie, radar, heatmap, and force-graph views.

## Structure

```
app/
  layout.tsx            root shell: sidebar + topbar + fonts
  globals.css           design tokens / base styles
  page.tsx               Home Dashboard
  company-intelligence/  Company Intelligence
  trust-analytics/       Trust Analytics
  risk-center/           Risk Center
  knowledge-graph/       Knowledge Graph Explorer
  ai-copilot/            AI Copilot
  executive-reports/     Executive Reports
components/
  layout/                Sidebar, Topbar
  ui/                    shadcn-style primitives (card, badge, button, tabs, progress)
  charts/                Shared ECharts wrapper + theme
  dashboard/             KpiCard, PageHeader, DataTable, CopilotChat
lib/
  utils.ts               cn() + number/formatting helpers
```

## Wiring to real data

Every page currently renders realistic mock data defined at the top of
its `page.tsx` file. To connect live data:

1. Replace the local arrays (`signals`, `companies`, `incidents`,
   `reports`, graph `nodes`/`links`, etc.) with fetches to your API —
   these pages are server components by default, so use `async` +
   `fetch()` directly, or convert to client components with your data
   hooks of choice.
2. The `CopilotChat` component (`components/dashboard/copilot-chat.tsx`)
   posts nowhere yet — wire its `send()` function to your inference
   endpoint.
3. `EChart` accepts any valid ECharts `option`, so existing chart shapes
   (line, bar, pie, radar, heatmap, graph) can be re-pointed at live
   series without touching the theme.
