'use client'

import Link from 'next/link'
import { useState } from 'react'

export default function APIKeysPage() {
  const [keys, setKeys] = useState<any[]>([])
  const [generating, setGenerating] = useState(false)
  const [newKey, setNewKey] = useState<string | null>(null)

  const generateKey = () => {
    setGenerating(true)
    // Simulate API key generation
    setTimeout(() => {
      const key = `ck_${Math.random().toString(36).substr(2, 9)}_${Math.random().toString(36).substr(2, 32)}`
      setNewKey(key)
      setKeys([...keys, {
        id: keys.length + 1,
        key,
        name: `API Key ${keys.length + 1}`,
        created: new Date().toISOString(),
        lastUsed: null,
        requests: 0
      }])
      setGenerating(false)
    }, 1500)
  }

  const copyKey = (key: string) => {
    navigator.clipboard.writeText(key)
    alert('API key copied to clipboard!')
  }

  const revokeKey = (id: number) => {
    if (confirm('Are you sure you want to revoke this API key? This action cannot be undone.')) {
      setKeys(keys.filter(k => k.id !== id))
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="text-2xl font-black bg-gradient-to-r from-amber-400 to-amber-600 bg-clip-text text-transparent">
              CLARITY
            </div>
            <span className="text-sm text-slate-400">API Keys</span>
          </Link>
          <div className="flex items-center gap-4">
            <Link
              href="/docs"
              className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-lg transition-all text-sm"
            >
              API Docs
            </Link>
            <Link
              href="/work"
              className="px-4 py-2 bg-amber-500 hover:bg-amber-400 text-slate-900 font-bold rounded-lg transition-all text-sm"
            >
              Dashboard
            </Link>
          </div>
        </div>
      </header>

      <div className="max-w-7xl mx-auto px-4 py-12">
        {/* Hero */}
        <div className="mb-12">
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-blue-500/20 border border-blue-500/30 text-blue-200 text-sm font-semibold mb-6">
            <span>🔑</span>
            <span>API KEY MANAGEMENT</span>
          </div>
          <h1 className="text-5xl md:text-6xl font-black mb-6 text-white">
            Your API Keys
          </h1>
          <p className="text-xl text-slate-300 max-w-3xl">
            Generate and manage API keys to integrate CLARITY into your applications. Keep your keys secure and never share them publicly.
          </p>
        </div>

        {/* New Key Alert */}
        {newKey && (
          <div className="mb-8 p-6 rounded-2xl bg-green-500/10 border-2 border-green-500/50 animate-pulse">
            <div className="flex items-start gap-4">
              <div className="text-4xl">✅</div>
              <div className="flex-1">
                <h3 className="text-xl font-bold text-green-400 mb-2">API Key Generated!</h3>
                <p className="text-slate-300 mb-4">
                  Save this key now! For security reasons, you won't be able to see it again.
                </p>
                <div className="flex items-center gap-3">
                  <code className="flex-1 px-4 py-3 bg-slate-950 text-green-400 rounded-lg text-sm font-mono overflow-x-auto">
                    {newKey}
                  </code>
                  <button
                    onClick={() => copyKey(newKey)}
                    className="px-4 py-3 bg-green-500 hover:bg-green-400 text-white font-bold rounded-lg transition-all"
                  >
                    Copy
                  </button>
                </div>
              </div>
              <button
                onClick={() => setNewKey(null)}
                className="text-slate-400 hover:text-white text-2xl"
              >
                ×
              </button>
            </div>
          </div>
        )}

        {/* Generate New Key */}
        <div className="mb-8">
          <button
            onClick={generateKey}
            disabled={generating}
            className={`px-8 py-4 rounded-xl font-bold transition-all transform hover:scale-105 shadow-2xl ${
              generating
                ? 'bg-slate-700 text-slate-400 cursor-not-allowed'
                : 'bg-blue-500 hover:bg-blue-400 text-white'
            }`}
          >
            {generating ? (
              <>
                <span className="inline-block animate-spin mr-2">⚙️</span>
                Generating...
              </>
            ) : (
              <>
                + Generate New API Key
              </>
            )}
          </button>
        </div>

        {/* Keys List */}
        {keys.length === 0 ? (
          <div className="p-12 rounded-2xl bg-slate-800/30 border-2 border-dashed border-slate-700 text-center">
            <div className="text-6xl mb-4">🔑</div>
            <h3 className="text-2xl font-bold text-white mb-2">No API Keys Yet</h3>
            <p className="text-slate-400 mb-6">
              Generate your first API key to start integrating CLARITY
            </p>
            <button
              onClick={generateKey}
              className="px-6 py-3 bg-blue-500 hover:bg-blue-400 text-white font-bold rounded-lg transition-all"
            >
              Generate API Key
            </button>
          </div>
        ) : (
          <div className="space-y-4">
            {keys.map((key) => (
              <div
                key={key.id}
                className="p-6 rounded-2xl bg-slate-800/50 border border-slate-700 hover:border-blue-500/50 transition-all"
              >
                <div className="flex items-start gap-4">
                  <div className="flex-1">
                    <div className="flex items-center gap-3 mb-3">
                      <h3 className="text-xl font-bold text-white">{key.name}</h3>
                      <span className="px-3 py-1 rounded-full bg-green-500/20 text-green-400 text-xs font-bold">
                        ACTIVE
                      </span>
                    </div>
                    <div className="flex items-center gap-3 mb-4">
                      <code className="px-4 py-2 bg-slate-950 text-slate-400 rounded-lg text-sm font-mono">
                        {key.key.substring(0, 20)}...
                      </code>
                      <button
                        onClick={() => copyKey(key.key)}
                        className="px-3 py-2 bg-slate-700 hover:bg-slate-600 text-white text-sm rounded-lg transition-all"
                      >
                        Copy
                      </button>
                    </div>
                    <div className="grid grid-cols-3 gap-4 text-sm">
                      <div>
                        <p className="text-slate-500 mb-1">Created</p>
                        <p className="text-slate-300">{new Date(key.created).toLocaleDateString()}</p>
                      </div>
                      <div>
                        <p className="text-slate-500 mb-1">Last Used</p>
                        <p className="text-slate-300">{key.lastUsed || 'Never'}</p>
                      </div>
                      <div>
                        <p className="text-slate-500 mb-1">Requests</p>
                        <p className="text-slate-300">{key.requests.toLocaleString()}</p>
                      </div>
                    </div>
                  </div>
                  <button
                    onClick={() => revokeKey(key.id)}
                    className="px-4 py-2 bg-red-500/20 hover:bg-red-500/30 text-red-400 font-semibold rounded-lg transition-all text-sm"
                  >
                    Revoke
                  </button>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* Usage Info */}
        <div className="mt-12 grid md:grid-cols-2 gap-6">
          <div className="p-6 rounded-2xl bg-blue-500/10 border border-blue-500/30">
            <h3 className="text-xl font-bold text-blue-400 mb-4">📖 How to Use Your API Key</h3>
            <div className="space-y-3 text-sm text-slate-300">
              <p>1. Include your API key in the <code className="text-green-400">Authorization</code> header:</p>
              <div className="bg-slate-950 p-3 rounded-lg overflow-x-auto">
                <pre className="text-xs text-green-400">
{`curl -X POST https://veritas-engine-zae0.onrender.com/instant/analyze \\
  -H "Authorization: Bearer YOUR_API_KEY" \\
  -H "Content-Type: application/json" \\
  -d '{"directive": "...", "domain": "legal"}'`}
                </pre>
              </div>
              <p>2. Keep your key secure and never commit it to public repositories</p>
              <p>3. Rotate keys regularly for security</p>
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-amber-500/10 border border-amber-500/30">
            <h3 className="text-xl font-bold text-amber-400 mb-4">⚠️ Security Best Practices</h3>
            <ul className="space-y-2 text-sm text-slate-300">
              <li className="flex items-start gap-2">
                <span className="text-amber-400 mt-1">•</span>
                <span>Never share your API keys publicly or in client-side code</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-amber-400 mt-1">•</span>
                <span>Use environment variables to store keys</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-amber-400 mt-1">•</span>
                <span>Rotate keys if you suspect they've been compromised</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-amber-400 mt-1">•</span>
                <span>Monitor usage and revoke unused keys</span>
              </li>
              <li className="flex items-start gap-2">
                <span className="text-amber-400 mt-1">•</span>
                <span>Use different keys for different environments (dev, staging, prod)</span>
              </li>
            </ul>
          </div>
        </div>

        {/* Rate Limits */}
        <div className="mt-12 p-8 rounded-2xl bg-slate-800/50 border border-purple-500/30">
          <h2 className="text-3xl font-bold text-white mb-6">Rate Limits by Tier</h2>
          <div className="grid md:grid-cols-3 gap-6">
            <div className="p-6 rounded-xl bg-slate-900/50">
              <h3 className="text-xl font-bold text-slate-400 mb-4">Free</h3>
              <div className="text-4xl font-black text-white mb-2">100</div>
              <p className="text-slate-400 mb-4">requests/hour</p>
              <p className="text-sm text-slate-500">No API key required</p>
            </div>
            <div className="p-6 rounded-xl bg-blue-500/20 border border-blue-500/50">
              <h3 className="text-xl font-bold text-blue-400 mb-4">Pro</h3>
              <div className="text-4xl font-black text-white mb-2">1,000</div>
              <p className="text-slate-300 mb-4">requests/hour</p>
              <Link
                href="/#pricing"
                className="block text-center px-4 py-2 bg-blue-500 hover:bg-blue-400 text-white font-bold rounded-lg transition-all text-sm"
              >
                Upgrade to Pro
              </Link>
            </div>
            <div className="p-6 rounded-xl bg-purple-500/20 border border-purple-500/50">
              <h3 className="text-xl font-bold text-purple-400 mb-4">Enterprise</h3>
              <div className="text-4xl font-black text-white mb-2">∞</div>
              <p className="text-slate-300 mb-4">Unlimited</p>
              <a
                href="mailto:nsubugacollin@gmail.com?subject=Enterprise API Access"
                className="block text-center px-4 py-2 bg-purple-500 hover:bg-purple-400 text-white font-bold rounded-lg transition-all text-sm"
              >
                Contact Sales
              </a>
            </div>
          </div>
        </div>

        {/* CTA */}
        <div className="mt-12 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">Need Help?</h2>
          <p className="text-slate-300 mb-6">Check out our API documentation or contact support</p>
          <div className="flex items-center justify-center gap-4">
            <Link
              href="/docs"
              className="px-8 py-4 bg-blue-500 hover:bg-blue-400 text-white font-bold rounded-xl transition-all transform hover:scale-105 shadow-2xl"
            >
              View API Docs
            </Link>
            <a
              href="mailto:nsubugacollin@gmail.com"
              className="px-8 py-4 bg-slate-700 hover:bg-slate-600 text-white font-bold rounded-xl transition-all"
            >
              Contact Support
            </a>
          </div>
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
            <Link href="/docs" className="hover:text-amber-400">API Docs</Link>
            <a href="mailto:nsubugacollin@gmail.com" className="hover:text-amber-400">Contact</a>
          </div>
        </div>
      </footer>
    </div>
  )
}
