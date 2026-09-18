import { PageHeader } from "@/components/dashboard/page-header";
import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
import { Badge } from "@/components/ui/badge";
import { CopilotChat } from "@/components/dashboard/copilot-chat";
import { Database, FileText, Link2 } from "lucide-react";

export default function AiCopilotPage() {
  return (
    <div className="pb-10 h-full flex flex-col">
      <PageHeader
        title="AI Copilot"
        description="A grounded assistant with live access to your intelligence graph, risk models, and filings."
      />

      <div className="grid grid-cols-1 xl:grid-cols-4 gap-3 px-6 flex-1 min-h-[560px]">
        <Card className="xl:col-span-3 flex flex-col overflow-hidden">
          <CardHeader>
            <div>
              <CardTitle>Copilot session</CardTitle>
              <CardDescription>Grounded in portfolio data · responses cite sources</CardDescription>
            </div>
            <Badge variant="signal" dot>Model: RitaDrishti-Reasoning v2</Badge>
          </CardHeader>
          <div className="flex-1 min-h-0">
            <CopilotChat />
          </div>
        </Card>

        <div className="space-y-3">
          <Card>
            <CardHeader>
              <CardTitle>Grounded on</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2.5">
              <div className="flex items-center gap-2.5 text-[13px] text-ink-100">
                <Database className="h-3.5 w-3.5 text-signal" />
                Knowledge graph
                <span className="ml-auto text-2xs text-ink-600">live</span>
              </div>
              <div className="flex items-center gap-2.5 text-[13px] text-ink-100">
                <FileText className="h-3.5 w-3.5 text-signal" />
                Filings & documents
                <span className="ml-auto text-2xs text-ink-600">4,201 docs</span>
              </div>
              <div className="flex items-center gap-2.5 text-[13px] text-ink-100">
                <Link2 className="h-3.5 w-3.5 text-signal" />
                Risk model outputs
                <span className="ml-auto text-2xs text-ink-600">live</span>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Session context</CardTitle>
            </CardHeader>
            <CardContent className="space-y-2 text-2xs text-ink-400">
              <div className="flex justify-between">
                <span>Scope</span>
                <span className="text-ink-100">Full portfolio</span>
              </div>
              <div className="flex justify-between">
                <span>Access level</span>
                <span className="text-ink-100">Executive</span>
              </div>
              <div className="flex justify-between">
                <span>Citations</span>
                <span className="text-ink-100">Enabled</span>
              </div>
              <div className="flex justify-between">
                <span>Retention</span>
                <span className="text-ink-100">Session only</span>
              </div>
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
