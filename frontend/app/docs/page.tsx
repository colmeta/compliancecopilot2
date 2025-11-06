'use client'

import Link from 'next/link'
import { useState } from 'react'

export default function APIDocumentation() {
  const [selectedEndpoint, setSelectedEndpoint] = useState('analyze')

  const endpoints = {
    analyze: {
      method: 'POST',
      path: '/instant/analyze',
      description: 'Submit a directive for instant AI analysis across any domain',
      request: {
        directive: 'string (required) - Your analysis request',
        domain: 'string (required) - One of: legal, financial, security, healthcare, data-science, education, proposals, ngo, data-entry, expenses',
        files: 'array (optional) - File data for document analysis'
      },
      response: `{
  "success": true,
  "task_id": "uuid",
  "domain": "legal",
  "directive": "Review contract...",
  "analysis": {
    "summary": "Legal Intelligence Analysis",
    "findings": [
      "Contract structure appears standard",
      "No obvious red flags detected",
      "Recommend detailed review of liability clauses"
    ],
    "confidence": 0.85,
    "next_steps": "Full analysis requires 5-10 minutes"
  },
  "status": "instant_preview",
  "timestamp": "2025-11-06T14:45:04.472132"
}`,
      example: `curl -X POST https://veritas-engine-zae0.onrender.com/instant/analyze \\
  -H "Content-Type: application/json" \\
  -d '{
    "directive": "Review this contract for liability risks and payment terms",
    "domain": "legal"
  }'`
    },
    domains: {
      method: 'GET',
      path: '/instant/domains',
      description: 'List all available analysis domains',
      request: null,
      response: `{
  "domains": [
    {
      "id": "legal",
      "name": "Legal Intelligence",
      "description": "Contract review, compliance checks, risk analysis",
      "icon": "⚖️"
    },
    {
      "id": "financial",
      "name": "Financial Intelligence",
      "description": "Financial analysis, anomaly detection, audit support",
      "icon": "💰"
    }
    // ... 8 more domains
  ],
  "total": 10,
  "note": "All domains available on free tier with instant previews"
}`,
      example: `curl https://veritas-engine-zae0.onrender.com/instant/domains`
    },
    health: {
      method: 'GET',
      path: '/instant/health',
      description: 'Check API health and status',
      request: null,
      response: `{
  "status": "healthy",
  "service": "CLARITY Engine (Free Tier)",
  "version": "1.0.0"
}`,
      example: `curl https://veritas-engine-zae0.onrender.com/instant/health`
    }
  }

  const currentEndpoint = endpoints[selectedEndpoint as keyof typeof endpoints]

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="text-2xl font-black bg-gradient-to-r from-amber-400 to-amber-600 bg-clip-text text-transparent">
              CLARITY
            </div>
            <span className="text-sm text-slate-400">API Documentation</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link
              href="/api-keys"
              className="px-4 py-2 bg-blue-500 hover:bg-blue-400 text-white font-bold rounded-lg transition-all text-sm"
            >
              Get API Key
            </Link>
            <Link
              href="/work"
              className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-900 font-bold rounded-lg transition-all text-sm"
            >
              Try Live
            </Link>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* Hero */}
        <div className="mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/20 border border-blue-500/30 text-blue-200 text-sm font-semibold mb-6">
            <span>🔌</span>
            <span>REST API</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-black mb-6 text-white">
            CLARITY API<br/>
            <span className="text-blue-400">Documentation</span>
          </h1>
          <p className="text-xl text-slate-300 max-w-3xl">
            RESTful API for enterprise-grade AI intelligence. Analyze documents, extract insights, and automate workflows across 10 specialized domains.
          </p>
        </div>

        {/* Quick Start */}
        <div className="mb-12 p-8 rounded-2xl bg-slate-800/50 border border-blue-500/30">
          <h2 className="text-3xl font-bold text-white mb-6">Quick Start</h2>
          <div className="grid md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-xl font-bold text-blue-400 mb-3">1. Base URL</h3>
              <code className="block px-4 py-2 bg-slate-950 text-green-400 rounded-lg text-sm">
                https://veritas-engine-zae0.onrender.com
              </code>
            </div>
            <div>
              <h3 className="text-xl font-bold text-blue-400 mb-3">2. Authentication</h3>
              <p className="text-slate-300 text-sm">
                Free tier: No authentication required<br/>
                Paid tier: API key in <code className="text-green-400">Authorization</code> header
              </p>
            </div>
          </div>
          <div className="mt-6">
            <h3 className="text-xl font-bold text-blue-400 mb-3">3. Make Your First Request</h3>
            <div className="bg-slate-950 p-4 rounded-lg overflow-x-auto">
              <pre className="text-sm text-green-400 whitespace-pre-wrap">
{`curl -X POST https://veritas-engine-zae0.onrender.com/instant/analyze \\
  -H "Content-Type: application/json" \\
  -d '{
    "directive": "Analyze financial statements for anomalies",
    "domain": "financial"
  }'`}
              </pre>
            </div>
          </div>
        </div>

        {/* Endpoints */}
        <div className="grid md:grid-cols-4 gap-6">
          {/* Sidebar */}
          <div className="md:col-span-1">
            <div className="sticky top-24">
              <h3 className="text-xl font-bold text-white mb-4">Endpoints</h3>
              <div className="space-y-2">
                {Object.keys(endpoints).map((key) => (
                  <button
                    key={key}
                    onClick={() => setSelectedEndpoint(key)}
                    className={`w-full text-left px-4 py-3 rounded-lg transition-all ${
                      selectedEndpoint === key
                        ? 'bg-blue-500 text-white font-bold'
                        : 'bg-slate-800/50 text-slate-300 hover:bg-slate-800'
                    }`}
                  >
                    <div className="text-xs text-slate-400">{endpoints[key as keyof typeof endpoints].method}</div>
                    <div className="text-sm">{endpoints[key as keyof typeof endpoints].path}</div>
                  </button>
                ))}
              </div>

              <div className="mt-8 p-4 rounded-lg bg-amber-500/10 border border-amber-500/30">
                <h4 className="text-sm font-bold text-amber-400 mb-2">Need Help?</h4>
                <p className="text-xs text-slate-300 mb-3">Contact our support team</p>
                <a
                  href="mailto:nsubugacollin@gmail.com"
                  className="text-xs text-blue-400 hover:text-blue-300"
                >
                  nsubugacollin@gmail.com
                </a>
              </div>
            </div>
          </div>

          {/* Content */}
          <div className="md:col-span-3">
            <div className="p-8 rounded-2xl bg-slate-800/50 border border-slate-700">
              <div className="flex items-center gap-3 mb-6">
                <span className={`px-3 py-1 rounded-full text-xs font-bold ${
                  currentEndpoint.method === 'POST' ? 'bg-green-500/20 text-green-400' : 'bg-blue-500/20 text-blue-400'
                }`}>
                  {currentEndpoint.method}
                </span>
                <code className="text-xl font-mono text-white">{currentEndpoint.path}</code>
              </div>

              <p className="text-slate-300 mb-8">{currentEndpoint.description}</p>

              {/* Request */}
              {currentEndpoint.request && (
                <div className="mb-8">
                  <h3 className="text-xl font-bold text-white mb-4">Request Body</h3>
                  <div className="bg-slate-950 p-4 rounded-lg">
                    <pre className="text-sm text-slate-300">
                      {JSON.stringify(currentEndpoint.request, null, 2)}
                    </pre>
                  </div>
                </div>
              )}

              {/* Response */}
              <div className="mb-8">
                <h3 className="text-xl font-bold text-white mb-4">Response</h3>
                <div className="bg-slate-950 p-4 rounded-lg overflow-x-auto">
                  <pre className="text-sm text-green-400 whitespace-pre-wrap">
                    {currentEndpoint.response}
                  </pre>
                </div>
              </div>

              {/* Example */}
              <div>
                <h3 className="text-xl font-bold text-white mb-4">Example Request</h3>
                <div className="bg-slate-950 p-4 rounded-lg overflow-x-auto">
                  <pre className="text-sm text-green-400 whitespace-pre-wrap">
                    {currentEndpoint.example}
                  </pre>
                </div>
              </div>
            </div>

            {/* SDKs */}
            <div className="mt-8 p-8 rounded-2xl bg-gradient-to-r from-purple-500/10 to-blue-500/10 border border-purple-500/30">
              <h3 className="text-2xl font-bold text-white mb-6">Official SDKs (Coming Soon)</h3>
              <div className="grid md:grid-cols-3 gap-4">
                <div className="p-4 rounded-lg bg-slate-900/50">
                  <div className="text-3xl mb-2">🐍</div>
                  <h4 className="font-bold text-white mb-1">Python</h4>
                  <code className="text-xs text-green-400">pip install clarity-ai</code>
                </div>
                <div className="p-4 rounded-lg bg-slate-900/50">
                  <div className="text-3xl mb-2">📜</div>
                  <h4 className="font-bold text-white mb-1">JavaScript</h4>
                  <code className="text-xs text-green-400">npm install @clarity/sdk</code>
                </div>
                <div className="p-4 rounded-lg bg-slate-900/50">
                  <div className="text-3xl mb-2">🐹</div>
                  <h4 className="font-bold text-white mb-1">Go</h4>
                  <code className="text-xs text-green-400">go get clarity.ai/sdk</code>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Rate Limits */}
        <div className="mt-12 p-8 rounded-2xl bg-slate-800/50 border border-amber-500/30">
          <h2 className="text-3xl font-bold text-white mb-6">Rate Limits</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div>
              <h3 className="text-xl font-bold text-amber-400 mb-2">Free Tier</h3>
              <p className="text-slate-300">100 requests/hour</p>
              <p className="text-slate-400 text-sm">No authentication required</p>
            </div>
            <div>
              <h3 className="text-xl font-bold text-blue-400 mb-2">Pro Tier</h3>
              <p className="text-slate-300">1,000 requests/hour</p>
              <p className="text-slate-400 text-sm">API key required</p>
            </div>
            <div>
              <h3 className="text-xl font-bold text-purple-400 mb-2">Enterprise</h3>
              <p className="text-slate-300">Unlimited</p>
              <p className="text-slate-400 text-sm">Custom SLA</p>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="mt-12 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Ready to Build?</h2>
          <p className="text-slate-300 mb-6">Get your API key and start integrating CLARITY today</p>
          <Link
            href="/api-keys"
            className="inline-block px-8 py-4 bg-blue-500 hover:bg-blue-400 text-white font-bold rounded-xl transition-all transform hover:scale-105 shadow-2xl"
          >
            Generate API Key →
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-white/10 bg-slate-900/95 mt-24 py-12 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-slate-400">
            © 2025 Clarity Pearl. All rights reserved.
          </p>
          <div className="mt-4 flex items-center justify-center gap-6 text-slate-400 text-sm">
            <Link href="/" className="hover:text-amber-400">Home</Link>
            <Link href="/work" className="hover:text-amber-400">Platform</Link>
            <a href="mailto:nsubugacollin@gmail.com" className="hover:text-amber-400">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  )
}
