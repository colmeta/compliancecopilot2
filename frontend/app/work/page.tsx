'use client'

import { useState, Suspense } from 'react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'

// Backend API URL
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'https://veritas-faxh.onrender.com'

function CommandDeckContent() {
  const searchParams = useSearchParams()
  const initialDomain = searchParams?.get('domain') || 'legal'
  
  const [selectedDomain, setSelectedDomain] = useState(initialDomain)
  const [directive, setDirective] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [submitted, setSubmitted] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [taskId, setTaskId] = useState('')
  const [analysis, setAnalysis] = useState<any>(null)
  const [error, setError] = useState('')

  const domains: Record<string, any> = {
    legal: { name: 'Legal Intelligence', icon: '⚖️', color: 'from-blue-500 to-cyan-500' },
    financial: { name: 'Financial Intelligence', icon: '💰', color: 'from-green-500 to-emerald-500' },
    security: { name: 'Security Intelligence', icon: '🔐', color: 'from-red-500 to-pink-500' },
    healthcare: { name: 'Healthcare Intelligence', icon: '🏥', color: 'from-purple-500 to-violet-500' },
    'data-science': { name: 'Data Science Engine', icon: '📊', color: 'from-amber-500 to-orange-500' },
    education: { name: 'Education Intelligence', icon: '🎓', color: 'from-indigo-500 to-blue-500' },
    proposals: { name: 'Proposal Writing', icon: '✍️', color: 'from-teal-500 to-cyan-500' },
    ngo: { name: 'NGO & Impact', icon: '🌍', color: 'from-lime-500 to-green-500' },
    'data-entry': { name: 'Data Entry Automation', icon: '🏢', color: 'from-slate-500 to-gray-500' },
    expenses: { name: 'Expense Management', icon: '💳', color: 'from-rose-500 to-red-500' },
  }

  const currentDomain = domains[selectedDomain] || domains.legal

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files))
    }
  }

  const handleSubmit = async () => {
    if (!directive.trim()) {
      alert('Please enter a directive')
      return
    }

    setSubmitting(true)
    setError('')
    
    try {
      // Call real backend API
      const response = await fetch(`${BACKEND_URL}/instant/analyze`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          directive: directive,
          domain: selectedDomain
        })
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const result = await response.json()
      
      if (result.success) {
        setTaskId(result.task_id)
        setAnalysis(result.analysis)
        setSubmitted(true)
      } else {
        throw new Error(result.error || 'Analysis failed')
      }
    } catch (err: any) {
      console.error('Analysis error:', err)
      setError(err.message || 'Failed to connect to backend')
      alert(`Error: ${err.message}. Please try again.`)
    } finally {
      setSubmitting(false)
    }
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
        <header className="border-b border-white/10 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-50">
          <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
            <Link href="/" className="flex items-center gap-3">
              <div className="text-2xl font-black bg-gradient-to-r from-amber-400 to-amber-600 bg-clip-text text-transparent">
                CLARITY
              </div>
              <span className="text-sm text-slate-400">by Clarity Pearl</span>
            </Link>
          </div>
        </header>

        <main className="max-w-5xl mx-auto px-4 py-12">
          {/* Success Header */}
          <div className="text-center mb-12">
            <div className="text-6xl mb-6">✅</div>
            <h1 className="text-4xl md:text-5xl font-black mb-4 text-white">
              Analysis Complete!
            </h1>
            <p className="text-xl text-slate-300">
              <span className="text-amber-400 font-bold">{currentDomain.name}</span> instant preview is ready
            </p>
          </div>

          {/* Analysis Results */}
          {analysis && (
            <div className="bg-slate-800/50 rounded-2xl p-8 border border-white/10 backdrop-blur-xl mb-8">
              {/* Header */}
              <div className="flex items-start justify-between mb-6 pb-6 border-b border-white/10">
                <div className="flex-1">
                  <h2 className="text-3xl font-bold text-white mb-3">{analysis.summary}</h2>
                  <div className="flex items-center gap-4">
                    <span className="text-slate-400">Confidence Score:</span>
                    <span className="text-green-400 font-bold text-xl">{Math.round(analysis.confidence * 100)}%</span>
                    <div className="flex-1 max-w-xs h-2 bg-slate-700 rounded-full overflow-hidden">
                      <div 
                        className="h-full bg-green-500 rounded-full transition-all duration-500"
                        style={{ width: `${analysis.confidence * 100}%` }}
                      />
                    </div>
                  </div>
                </div>
              </div>

              {/* Findings */}
              <div className="mb-8">
                <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                  <span>🔍</span> Key Findings
                </h3>
                <ul className="space-y-3">
                  {analysis.findings.map((finding: string, index: number) => (
                    <li key={index} className="flex items-start gap-3 p-4 rounded-lg bg-slate-900/50">
                      <span className="text-blue-400 text-xl mt-0.5">•</span>
                      <span className="text-slate-300">{finding}</span>
                    </li>
                  ))}
                </ul>
              </div>

              {/* Next Steps */}
              <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-6 mb-8">
                <h3 className="text-lg font-bold text-blue-300 mb-2 flex items-center gap-2">
                  <span>📋</span> Recommended Next Steps
                </h3>
                <p className="text-slate-300">{analysis.next_steps}</p>
              </div>

              {/* Upgrade CTA */}
              <div className="bg-gradient-to-r from-purple-500/20 to-blue-500/20 border border-purple-500/30 rounded-xl p-8">
                <div className="flex items-start gap-4">
                  <div className="text-4xl">💎</div>
                  <div className="flex-1">
                    <h3 className="text-2xl font-bold text-white mb-3">Upgrade for Full AI Analysis</h3>
                    <p className="text-slate-300 mb-6">
                      This is an <strong>instant preview</strong>. Get the full power of CLARITY with:
                    </p>
                    <div className="grid md:grid-cols-2 gap-3 mb-6">
                      <div className="flex items-center gap-2 text-slate-300">
                        <span className="text-green-400">✓</span> Real Google Gemini AI processing
                      </div>
                      <div className="flex items-center gap-2 text-slate-300">
                        <span className="text-green-400">✓</span> Document upload & OCR
                      </div>
                      <div className="flex items-center gap-2 text-slate-300">
                        <span className="text-green-400">✓</span> Email delivery of results
                      </div>
                      <div className="flex items-center gap-2 text-slate-300">
                        <span className="text-green-400">✓</span> Detailed reports & citations
                      </div>
                    </div>
                    <button className="bg-gradient-to-r from-purple-600 to-blue-600 text-white px-8 py-4 rounded-xl font-bold text-lg hover:from-purple-700 hover:to-blue-700 transition-all shadow-lg">
                      Upgrade to Paid Tier →
                    </button>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Actions */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/"
              className="px-8 py-4 bg-slate-700 hover:bg-slate-600 text-white font-bold rounded-xl transition-all text-center"
            >
              ← Back to Home
            </Link>
            <button
              onClick={() => {
                setSubmitted(false)
                setDirective('')
                setFiles([])
                setTaskId('')
                setAnalysis(null)
              }}
              className="px-8 py-4 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-600 hover:to-amber-700 text-slate-900 font-bold rounded-xl transition-all"
            >
              Analyze Another Task
            </button>
          </div>

          {/* Task ID */}
          <div className="mt-8 text-center">
            <p className="text-slate-500 text-sm">
              Task ID: <span className="font-mono text-slate-400">{taskId}</span>
            </p>
          </div>
        </main>
      </div>
    )
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
            <span className="text-sm text-slate-400">by Clarity Pearl</span>
          </Link>
          <div className="flex items-center gap-6">
            <a href="mailto:nsubugacollin@gmail.com" className="text-slate-400 hover:text-white transition-colors text-sm">
              📧 Contact
            </a>
            <a href="tel:+256705885118" className="text-slate-400 hover:text-white transition-colors text-sm">
              📱 +256 705 885 118
            </a>
          </div>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-12">
        {/* Command Deck Header */}
        <div className="text-center mb-12">
          <h1 className="text-5xl md:text-6xl font-black mb-4 bg-gradient-to-r from-white via-blue-100 to-white bg-clip-text text-transparent">
            Command Deck
          </h1>
          <p className="text-xl text-slate-400">
            One interface. All domains. Presidential-grade intelligence.
          </p>
        </div>

        <div className="grid lg:grid-cols-3 gap-8">
          {/* Domain Selector - Left Sidebar */}
          <div className="lg:col-span-1">
            <div className="p-6 rounded-2xl bg-slate-800/50 border border-white/10 backdrop-blur-xl sticky top-24">
              <h2 className="text-lg font-bold text-white mb-4">Select Domain</h2>
              <div className="space-y-2">
                {Object.entries(domains).map(([key, domain]) => (
                  <button
                    key={key}
                    onClick={() => setSelectedDomain(key)}
                    className={`w-full text-left p-4 rounded-xl transition-all ${
                      selectedDomain === key
                        ? 'bg-gradient-to-r ' + domain.color + ' text-white shadow-lg'
                        : 'bg-slate-900/50 text-slate-300 hover:bg-slate-900 border border-slate-700'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">{domain.icon}</span>
                      <span className="font-semibold text-sm">{domain.name}</span>
                    </div>
                  </button>
                ))}
              </div>
            </div>
          </div>

          {/* Main Work Area - Right Side */}
          <div className="lg:col-span-2">
            <div className="p-8 rounded-2xl bg-slate-800/50 border border-white/10 backdrop-blur-xl">
              {/* Current Domain Header */}
              <div className="mb-8 pb-6 border-b border-white/10">
                <div className="flex items-center gap-4 mb-3">
                  <span className="text-5xl">{currentDomain.icon}</span>
                  <div>
                    <h2 className="text-3xl font-black text-white">{currentDomain.name}</h2>
                    <p className="text-slate-400">CLARITY Engine Active</p>
                  </div>
                </div>
              </div>

              {/* Directive Input */}
              <div className="mb-6">
                <label className="block text-white font-bold mb-3 text-lg">
                  What do you need? <span className="text-red-400">*</span>
                </label>
                <textarea
                  value={directive}
                  onChange={(e) => setDirective(e.target.value)}
                  placeholder="Tell CLARITY what you want analyzed, what insights you need, or what problems you're solving..."
                  className="w-full px-6 py-4 bg-slate-900/50 border border-slate-600 rounded-xl text-white placeholder-slate-500 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 transition-all resize-none text-lg"
                  rows={8}
                />
              </div>

              {/* File Upload */}
              <div className="mb-8">
                <label className="block text-white font-bold mb-3 text-lg">
                  Upload Documents (Optional)
                </label>
                <div className="border-2 border-dashed border-slate-600 rounded-xl p-8 text-center hover:border-amber-500 transition-all cursor-pointer">
                  <input
                    type="file"
                    multiple
                    onChange={handleFileChange}
                    className="hidden"
                    id="file-upload"
                  />
                  <label htmlFor="file-upload" className="cursor-pointer">
                    <div className="text-5xl mb-4">📎</div>
                    <p className="text-slate-300 mb-2 text-lg">Click to upload or drag files here</p>
                    <p className="text-slate-500">PDF, Word, Excel, Images, Audio, Video</p>
                  </label>
                </div>
                {files.length > 0 && (
                  <div className="mt-4 space-y-2">
                    {files.map((file, i) => (
                      <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-slate-900/50">
                        <span className="text-green-400 text-xl">✓</span>
                        <span className="text-slate-300 flex-1">{file.name}</span>
                        <span className="text-slate-500 text-sm">{(file.size / 1024).toFixed(1)} KB</span>
                      </div>
                    ))}
                  </div>
                )}
              </div>

              {/* Submit Button */}
              <button
                onClick={handleSubmit}
                disabled={submitting || (!directive.trim() && files.length === 0)}
                className="w-full py-5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 disabled:from-slate-700 disabled:to-slate-700 disabled:text-slate-500 text-slate-900 text-xl font-black rounded-xl transition-all transform hover:scale-[1.02] disabled:transform-none shadow-2xl"
              >
                {submitting ? 'Submitting...' : '🚀 Launch CLARITY Analysis'}
              </button>

              <p className="mt-4 text-center text-slate-400">
                📧 Results will be emailed to you (prevents browser crashes)
              </p>
            </div>
          </div>
        </div>
      </main>
    </div>
  )
}

export default function CommandDeck() {
  return (
    <Suspense fallback={
      <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
        <div className="text-white text-2xl">Loading CLARITY...</div>
      </div>
    }>
      <CommandDeckContent />
    </Suspense>
  )
}
