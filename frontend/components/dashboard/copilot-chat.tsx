"use client";

import { useState } from "react";
import { Sparkles, Send, User, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";
import { apiFetch } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  sources?: string[];
  isError?: boolean;
}

const INITIAL: Message[] = [
  {
    id: "m1",
    role: "assistant",
    content:
      "Hello! I am RitaDrishti AI Trust Copilot. I can assist with corporate risk audits, sentiment trends, fraud alerts, and vector search across company reviews and complaints.",
  }
];

const SUGGESTIONS = [
  "What are the main complaints against FinPay Tech?",
  "Show high-risk fintech companies with trust score > 60",
  "Analyze Acme Cloud Solutions trust metrics",
  "Which entities breached the risk threshold?",
];

export function CopilotChat() {
  const [messages, setMessages] = useState<Message[]>(INITIAL);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);

  async function send(text: string) {
    if (!text.trim() || loading) return;
    const userMsg: Message = { id: crypto.randomUUID(), role: "user", content: text };
    setMessages((m) => [...m, userMsg]);
    setInput("");
    setLoading(true);

    try {
      const data: any = await apiFetch("/api/v1/chat/", {
        method: "POST",
        body: JSON.stringify({ query: text })
      });

      const replyMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: data.answer || "Answer generated from vector retrieval.",
        sources: data.sources || []
      };
      setMessages((m) => [...m, replyMsg]);
    } catch (err: any) {
      const errorMsg: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: `⚠️ **API Service Notice**: ${err.message || "Request failed."}`,
        isError: true
      };
      setMessages((m) => [...m, errorMsg]);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="flex flex-col h-full">
      <div className="flex-1 overflow-y-auto px-5 py-4 space-y-4">
        {messages.map((m) => (
          <div
            key={m.id}
            className={cn("flex gap-3", m.role === "user" && "flex-row-reverse")}
          >
            <div
              className={cn(
                "flex h-7 w-7 shrink-0 items-center justify-center rounded-md border",
                m.role === "assistant"
                  ? m.isError ? "bg-rose-950 border-rose-800 text-rose-400" : "bg-signal-faint border-signal-dim/40 text-signal"
                  : "bg-graphite-700 border-line text-ink-400"
              )}
            >
              {m.role === "assistant" ? (
                <Sparkles className="h-3.5 w-3.5" />
              ) : (
                <User className="h-3.5 w-3.5" />
              )}
            </div>
            <div
              className={cn(
                "max-w-[80%] rounded-md px-3.5 py-2.5 text-[13px] leading-relaxed",
                m.role === "assistant"
                  ? m.isError ? "bg-rose-950/40 border border-rose-800/80 text-rose-300" : "bg-graphite-800 border border-line text-ink-100"
                  : "bg-signal/10 border border-signal-dim/30 text-ink-100"
              )}
            >
              <div className="whitespace-pre-wrap">{m.content}</div>
              {m.sources && m.sources.length > 0 && (
                <div className="mt-2 pt-2 border-t border-line/40 text-[11px] text-ink-500">
                  Sources: {m.sources.join(", ")}
                </div>
              )}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex gap-3 items-center text-ink-500 text-[12px] italic">
            <Loader2 className="h-4 w-4 animate-spin text-signal" />
            Querying backend RAG API endpoint...
          </div>
        )}
      </div>

      <div className="border-t border-line p-4 space-y-3">
        <div className="flex flex-wrap gap-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => send(s)}
              disabled={loading}
              className="text-2xs px-2.5 py-1.5 rounded-sm border border-line bg-graphite-800 text-ink-400 hover:text-ink-100 hover:bg-graphite-700 transition-colors disabled:opacity-50"
            >
              {s}
            </button>
          ))}
        </div>
        <form
          onSubmit={(e) => {
            e.preventDefault();
            send(input);
          }}
          className="flex items-center gap-2"
        >
          <input
            value={input}
            onChange={(e) => setInput(e.target.value)}
            disabled={loading}
            placeholder="Ask about an entity, signal, or trend…"
            className="flex-1 h-9 rounded-sm bg-graphite-800 border border-line px-3 text-[13px] text-ink-100 placeholder:text-ink-600 focus:outline-none focus:ring-1 focus:ring-signal"
          />
          <Button type="submit" size="icon" disabled={loading}>
            {loading ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <Send className="h-3.5 w-3.5" />}
          </Button>
        </form>
      </div>
    </div>
  );
}
