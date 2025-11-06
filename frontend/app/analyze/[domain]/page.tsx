'use client'

import { useState } from 'react'
import Link from 'next/link'
import { useParams } from 'next/navigation'

// Domain configurations
const DOMAIN_CONFIG: Record<string, any> = {
  legal: {
    name: 'Legal Intelligence',
    icon: '⚖️',
    color: 'from-blue-500 to-cyan-500',
    description: 'Contract analysis, compliance checking, legal research, risk assessment',
    examples: [
      'Review this contract and identify any non-standard liability clauses',
      'Analyze these legal documents for compliance with GDPR regulations',
      'Identify potential legal risks in this partnership agreement'
    ]
  },
  financial: {
    name: 'Financial Intelligence',
    icon: '💰',
    color: 'from-green-500 to-emerald-500',
    description: 'Financial modeling, forecasting, analysis, expense management',
    examples: [
      'Audit these financial statements for anomalies',
      'Analyze spending patterns and identify cost reduction opportunities',
      'Review this budget and provide strategic recommendations'
    ]
  },
  security: {
    name: 'Security Intelligence',
    icon: '🔐',
    color: 'from-red-500 to-pink-500',
    description: 'Threat detection, vulnerability assessment, compliance auditing',
    examples: [
      'Assess security vulnerabilities in this infrastructure document',
      'Analyze this incident report and provide mitigation strategies',
      'Review our security policies for compliance gaps'
    ]
  },
  healthcare: {
    name: 'Healthcare Intelligence',
    icon: '🏥',
    color: 'from-purple-500 to-violet-500',
    description: 'Medical research, patient analysis, treatment planning, HIPAA compliance',
    examples: [
      'Analyze these patient records and identify treatment patterns',
      'Review our HIPAA compliance documentation for gaps',
      'Research treatment options for this medical case'
    ]
  },
  'data-science': {
    name: 'Data Science Engine',
    icon: '📊',
    color: 'from-amber-500 to-orange-500',
    description: 'Presidential briefings, World Bank insights, IMF-grade forecasts',
    examples: [
      'Analyze this economic data and generate presidential-level insights',
      'Create a World Bank-style development report from this data',
      'Generate IMF-grade economic forecasts from these trends'
    ]
  },
  education: {
    name: 'Education Intelligence',
    icon: '🎓',
    color: 'from-indigo-500 to-blue-500',
    description: 'Curriculum analysis, accreditation reports, grant proposals',
    examples: [
      'Analyze our curriculum against accreditation standards',
      'Review these student performance metrics and identify improvement areas',
      'Draft an accreditation self-study report from our documents'
    ]
  },
  proposals: {
    name: 'Proposal Writing Excellence',
    icon: '✍️',
    color: 'from-teal-500 to-cyan-500',
    description: 'RFPs, grants, partnerships, tenders - Win every bid',
    examples: [
      'Write a compelling RFP response for this government contract',
      'Draft a grant proposal for this NGO project',
      'Create a partnership proposal for this corporate opportunity'
    ]
  },
  ngo: {
    name: 'NGO & Impact Intelligence',
    icon: '🌍',
    color: 'from-lime-500 to-green-500',
    description: 'Grant proposals, impact reports, donor communications',
    examples: [
      'Generate an impact assessment report from our program data',
      'Write a donor communication highlighting our achievements',
      'Draft a grant proposal for our education initiative'
    ]
  },
  'data-entry': {
    name: 'Data Entry Automation',
    icon: '🏢',
    color: 'from-slate-500 to-gray-500',
    description: '4-agent system: Vision → Extraction → Validation → Loading',
    examples: [
      'Extract data from these scanned invoices into our database',
      'Process these paper forms and validate the information',
      'Convert these PDF receipts into structured data'
    ]
  },
  expenses: {
    name: 'Expense Management',
    icon: '💳',
    color: 'from-rose-500 to-red-500',
    description: 'Receipt scanning, expense tracking, budget balancing, cost reduction',
    examples: [
      'Analyze our monthly expenses and identify cost-saving opportunities',
      'Categorize these receipts and balance against our budget',
      'Track our spending by department and flag anomalies'
    ]
  }
}

export default function DomainAnalysisPage() {
  const params = useParams()
  const domain = params?.domain as string
  const config = DOMAIN_CONFIG[domain] || DOMAIN_CONFIG.legal // Fallback
  
  const [directive, setDirective] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [submitted, setSubmitted] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [taskId, setTaskId] = useState('')

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
      // const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/analyze`, {
      //   method: 'POST',
      //   body: formData
      // })
      
      // Simulate submission
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
            <Link href="/dashboard" className="text-slate-400 hover:text-amber-400 transition-colors">
              ← Back to Dashboard
            </Link>
          </div>
        </header>

        <main className="max-w-3xl mx-auto px-4 py-20 text-center">
          <div className="text-6xl mb-6">✅</div>
          <h1 className="text-4xl md:text-5xl font-black mb-6 text-white">
            Task Submitted Successfully!
          </h1>
          <p className="text-xl text-slate-300 mb-12 max-w-2xl mx-auto">
            Your <span className="text-amber-400 font-bold">{config.name}</span> analysis is being processed in the background.
          </p>

          <div className="p-8 rounded-2xl bg-slate-800/50 border border-green-500/30 backdrop-blur-xl mb-8">
            <p className="text-lg text-slate-300 mb-4">
              <span className="text-green-400 font-bold">You can close this browser!</span>
            </p>
            <p className="text-slate-400 mb-6">
              We'll email you when your results are ready. This prevents browser timeouts and allows our system to handle unlimited concurrent users without crashes.
            </p>
            <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/30">
              <p className="text-blue-300 text-sm"><strong>Task ID:</strong> {taskId}</p>
              <p className="text-blue-300 text-sm mt-2"><strong>Estimated Time:</strong> 5-15 minutes</p>
            </div>
          </div>

          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link
              href="/dashboard"
              className="px-8 py-4 bg-slate-700 hover:bg-slate-600 text-white font-bold rounded-xl transition-all"
            >
              Back to Dashboard
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
          <Link href="/dashboard" className="text-slate-400 hover:text-amber-400 transition-colors">
            ← Back to Dashboard
          </Link>
        </div>
      </header>

      <main className="max-w-5xl mx-auto px-4 py-12">
        {/* Domain Header */}
        <div className="text-center mb-12">
          <div className="text-6xl mb-4">{config.icon}</div>
          <h1 className="text-4xl md:text-5xl font-black mb-4 bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
            {config.name}
          </h1>
          <p className="text-xl text-slate-400 max-w-2xl mx-auto">
            {config.description}
          </p>
        </div>

        {/* Main Work Interface */}
        <div className="p-8 rounded-2xl bg-slate-800/50 border border-white/10 backdrop-blur-xl mb-8">
          <h2 className="text-2xl font-bold text-white mb-6">What do you need analyzed?</h2>

          {/* Directive Input */}
          <div className="mb-6">
            <label className="block text-slate-300 font-semibold mb-3">
              Your Directive <span className="text-red-400">*</span>
            </label>
            <textarea
              value={directive}
              onChange={(e) => setDirective(e.target.value)}
              placeholder="Tell CLARITY what you want analyzed, what insights you need, or what problems you're solving..."
              className="w-full px-6 py-4 bg-slate-900/50 border border-slate-600 rounded-xl text-white placeholder-slate-500 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 transition-all resize-none"
              rows={6}
            />
          </div>

          {/* File Upload */}
          <div className="mb-6">
            <label className="block text-slate-300 font-semibold mb-3">
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
                <div className="text-4xl mb-3">📎</div>
                <p className="text-slate-300 mb-2">Click to upload or drag files here</p>
                <p className="text-slate-500 text-sm">PDF, Word, Excel, Images, Audio, Video</p>
              </label>
            </div>
            {files.length > 0 && (
              <div className="mt-4 space-y-2">
                {files.map((file, i) => (
                  <div key={i} className="flex items-center gap-3 p-3 rounded-lg bg-slate-900/50">
                    <span className="text-green-400">✓</span>
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
            className="w-full py-4 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 disabled:from-slate-700 disabled:to-slate-700 disabled:text-slate-500 text-slate-900 text-lg font-black rounded-xl transition-all transform hover:scale-[1.02] disabled:transform-none shadow-lg"
          >
            {submitting ? 'Submitting...' : 'Analyze with CLARITY →'}
          </button>

          <p className="mt-4 text-center text-slate-400 text-sm">
            📧 Results will be emailed to you (prevents browser crashes)
          </p>
        </div>

        {/* Example Directives */}
        <div className="p-6 rounded-xl bg-slate-800/30 border border-white/5">
          <h3 className="text-lg font-bold text-white mb-4">Example Directives:</h3>
          <div className="space-y-2">
            {config.examples.map((example: string, i: number) => (
              <button
                key={i}
                onClick={() => setDirective(example)}
                className="block w-full text-left p-4 rounded-lg bg-slate-900/50 hover:bg-slate-900 border border-slate-700 hover:border-amber-500 text-slate-300 transition-all"
              >
                <span className="text-amber-400 mr-2">💡</span>
                {example}
              </button>
            ))}
          </div>
        </div>
      </main>
    </div>
  )
}
