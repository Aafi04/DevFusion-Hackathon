"use client";

import { useState } from "react";
import Link from "next/link";
import {
  Database,
  ArrowRight,
  Sparkles,
  GitFork,
  MessageSquare,
  ShieldCheck,
  FileText,
  BarChart3,
  Play,
  X,
  Info,
} from "lucide-react";

export default function Home() {
  const [showDemo, setShowDemo] = useState(false);

  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-zinc-950 px-6">
      {/* Gradient Glow */}
      <div className="pointer-events-none absolute inset-0 overflow-hidden">
        <div className="absolute left-1/2 top-1/3 h-96 w-96 -translate-x-1/2 -translate-y-1/2 rounded-full bg-blue-600/10 blur-3xl" />
      </div>

      {/* Demo Video Modal */}
      {showDemo && (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
          <div className="relative w-full max-w-4xl mx-4">
            <button
              onClick={() => setShowDemo(false)}
              className="absolute -top-10 right-0 flex items-center gap-1 text-sm text-zinc-400 hover:text-white transition-colors"
            >
              Close <X className="h-4 w-4" />
            </button>
            <div className="aspect-video w-full rounded-2xl overflow-hidden ring-1 ring-zinc-700 bg-zinc-900">
              <iframe
                src="https://drive.google.com/file/d/1KM8AKxEV_5BFxnViivPDXGUPn1hKWetu/preview"
                className="h-full w-full"
                allow="autoplay; encrypted-media"
                allowFullScreen
              />
            </div>
          </div>
        </div>
      )}

      <main className="relative z-10 flex max-w-4xl flex-col items-center text-center">
        {/* Logo */}
        <div className="mb-8 flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-500/10 ring-1 ring-blue-500/20">
          <Database className="h-8 w-8 text-blue-400" />
        </div>

        {/* Title */}
        <h1 className="text-5xl font-bold tracking-tight text-zinc-100">
          SchemaDoc{" "}
          <span className="bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
            AI
          </span>
        </h1>
        <p className="mt-4 max-w-lg text-lg text-zinc-400">
          AI-powered data dictionary generator that connects to enterprise
          databases, extracts schema metadata, analyzes data quality, and
          produces business-ready documentation.
        </p>

        {/* CTA */}
        <div className="mt-6 flex items-center gap-3">
          <Link
            href="/dashboard"
            className="flex items-center gap-2 rounded-xl bg-blue-600 px-6 py-3 text-sm font-semibold text-white transition-all hover:bg-blue-500 hover:shadow-lg hover:shadow-blue-500/20 active:scale-[0.98]"
          >
            Open Dashboard
            <ArrowRight className="h-4 w-4" />
          </Link>
          <button
            onClick={() =>
              window.open(
                "https://drive.google.com/file/d/1KM8AKxEV_5BFxnViivPDXGUPn1hKWetu/view",
                "_blank",
                "noopener,noreferrer",
              )
            }
            className="flex items-center gap-2 rounded-xl border border-zinc-700 bg-zinc-900 px-6 py-3 text-sm font-semibold text-zinc-200 transition-all hover:border-zinc-600 hover:bg-zinc-800 hover:shadow-lg active:scale-[0.98]"
          >
            <Play className="h-4 w-4 text-blue-400" />
            View Demo
          </button>
        </div>

        {/* Feature Cards */}
        <div className="mt-16 grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
          {[
            {
              icon: Sparkles,
              label: "AI Enrichment",
              desc: "Gemini 2.5 Flash with ReAct tool-calling",
            },
            {
              icon: ShieldCheck,
              label: "Anti-Hallucination",
              desc: "Deterministic validation gate with retry loop",
            },
            {
              icon: BarChart3,
              label: "Statistical Profiling",
              desc: "Null%, uniqueness, min/max/mean per column",
            },
            {
              icon: GitFork,
              label: "Knowledge Graph",
              desc: "Interactive ER diagrams with FK relationships",
            },
            {
              icon: MessageSquare,
              label: "NL→SQL Chat",
              desc: "Natural language to SQL query generation",
            },
            {
              icon: FileText,
              label: "Business Reports",
              desc: "AI-enhanced export in JSON & Markdown",
            },
          ].map((f) => (
            <div
              key={f.label}
              className="flex flex-col items-center gap-2 rounded-xl border border-zinc-800 bg-zinc-900/50 p-5 transition-colors hover:border-zinc-700"
            >
              <f.icon className="h-5 w-5 text-blue-400" />
              <span className="text-sm font-medium text-zinc-200">
                {f.label}
              </span>
              <span className="text-xs text-zinc-500">{f.desc}</span>
            </div>
          ))}
        </div>

        <p className="mt-12 text-xs text-zinc-600">
          Built for Hackfest 2.0 &mdash; Powered by LangGraph + Gemini + Next.js
        </p>
      </main>
    </div>
  );
}
