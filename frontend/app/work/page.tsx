'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'

// Backend API URL
const BACKEND_URL = 'https://veritas-engine-zae0.onrender.com'

export default function CommandDeck() {
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
    if (!directive.trim() && files.length === 0) {
      alert('Please provide a directive or upload files')
      return
    }

    setSubmitting(true)

    try {
      // TODO: Connect to backend API
      await new Promise(resolve => setTimeout(resolve, 1500))
      
      setSubmitted(true)
      setTaskId(`task_${Date.now()}`)
      setSubmitting(false)
    } catch (error) {
      console.error(error)
      alert('Submission failed. Please try again.')
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

        <main className="max-w-3xl mx-auto px-4 py-20 text-center">
          <div className="text-6xl mb-6">✅</div>
          <h1 className="text-4xl md:text-5xl font-black mb-6 text-white">
            Task Submitted Successfully!
          </h1>
          <p className="text-xl text-slate-300 mb-12">
            Your <span className="text-amber-400 font-bold">{currentDomain.name}</span> analysis is being processed.
          </p>

          <div className="p-8 rounded-2xl bg-slate-800/50 border border-green-500/30 backdrop-blur-xl mb-8">
            <p className="text-lg text-slate-300 mb-4">
              <span className="text-green-400 font-bold">✅ You can close this browser!</span>
            </p>
            <p className="text-slate-400 mb-6">
              We'll email you when your results are ready. This prevents browser timeouts and allows unlimited concurrent users.
            </p>
            <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/30">
              <p className="text-blue-300 text-sm"><strong>Task ID:</strong> {taskId}</p>
              <p className="text-blue-300 text-sm mt-2"><strong>Estimated Time:</strong> 5-15 minutes</p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/"
              className="px-8 py-4 bg-slate-700 hover:bg-slate-600 text-white font-bold rounded-xl transition-all"
            >
              ← Back to Home
            </Link>
            <button
              onClick={() => {
                setSubmitted(false)
                setDirective('')
                setFiles([])
                setTaskId('')
              }}
              className="px-8 py-4 bg-amber-500 hover:bg-amber-400 text-slate-900 font-bold rounded-xl transition-all"
            >
              Submit Another Task
            </button>
          </div>

          <div className="mt-12 p-6 rounded-xl bg-amber-500/10 border border-amber-500/30">
            <p className="text-amber-300 text-sm">
              📧 <strong>Check your email</strong> for results<br/>
              💡 <strong>Tip:</strong> Add noreply@claritypearl.com to your contacts
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
