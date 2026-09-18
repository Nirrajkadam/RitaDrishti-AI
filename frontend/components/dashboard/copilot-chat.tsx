"use client";

import { useState } from "react";
import { Sparkles, Send, User } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
}

const INITIAL: Message[] = [
  {
    id: "m1",
    role: "assistant",
    content:
      "I'm the RitaDrishti copilot. Ask me about any monitored entity, a risk signal, or request a summary across your portfolio.",
  },
  {
    id: "m2",
    role: "user",
    content: "Why did Vantage Freight's trust score drop this week?",
  },
  {
    id: "m3",
    role: "assistant",
    content:
      "Vantage Freight's trust score fell from 72 to 58 after the Q3 filing revealed a fuel-cost hedge mismatch. The model also flagged rising counterparty concentration on the north corridor route, which contributed 9 points of the decline. I'd recommend reviewing incident INC-2231 and the linked sanctions-proximity signal on Bharat Agrotech.",
  },
];

const SUGGESTIONS = [
  "Summarize this week's critical signals",
  "Compare trust scores across Logistics sector",
  "Draft a board-ready risk brief",
  "Which entities breached the 65 threshold?",
];

export function CopilotChat() {
  const [messages, setMessages] = useState<Message[]>(INITIAL);
  const [input, setInput] = useState("");

  function send(text: string) {
    if (!text.trim()) return;
    const userMsg: Message = { id: crypto.randomUUID(), role: "user", content: text };
    const reply: Message = {
      id: crypto.randomUUID(),
      role: "assistant",
      content:
        "Pulling from the latest intelligence graph and risk model outputs — I'll have a grounded answer with source citations shortly. (Demo response — connect the inference endpoint to enable live answers.)",
    };
    setMessages((m) => [...m, userMsg, reply]);
    setInput("");
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
                  ? "bg-signal-faint border-signal-dim/40 text-signal"
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
                "max-w-[75%] rounded-md px-3.5 py-2.5 text-[13px] leading-relaxed",
                m.role === "assistant"
                  ? "bg-graphite-800 border border-line text-ink-100"
                  : "bg-signal/10 border border-signal-dim/30 text-ink-100"
              )}
            >
              {m.content}
            </div>
          </div>
        ))}
      </div>

      <div className="border-t border-line p-4 space-y-3">
        <div className="flex flex-wrap gap-2">
          {SUGGESTIONS.map((s) => (
            <button
              key={s}
              onClick={() => send(s)}
              className="text-2xs px-2.5 py-1.5 rounded-sm border border-line bg-graphite-800 text-ink-400 hover:text-ink-100 hover:bg-graphite-700 transition-colors"
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
            placeholder="Ask about an entity, signal, or trend…"
            className="flex-1 h-9 rounded-sm bg-graphite-800 border border-line px-3 text-[13px] text-ink-100 placeholder:text-ink-600 focus:outline-none focus:ring-1 focus:ring-signal"
          />
          <Button type="submit" size="icon">
            <Send className="h-3.5 w-3.5" />
          </Button>
        </form>
      </div>
    </div>
  );
}
