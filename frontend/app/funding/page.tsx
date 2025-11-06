'use client'

import { useState } from 'react'
import Link from 'next/link'

type Step = 'welcome' | 'discovery' | 'configure' | 'generating' | 'results'

interface DiscoveryAnswers {
  [key: string]: string
}

interface DocumentConfig {
  fundingLevel: string
  targetAudience: string
  selectedDocuments: string[]
}

export default function FundingEngine() {
  const [step, setStep] = useState<Step>('welcome')
  const [discoveryAnswers, setDiscoveryAnswers] = useState<DiscoveryAnswers>({})
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [config, setConfig] = useState<DocumentConfig>({
    fundingLevel: 'seed',
    targetAudience: 'investors',
    selectedDocuments: []
  })
  const [generationProgress, setGenerationProgress] = useState(0)
  const [generatedDocuments, setGeneratedDocuments] = useState<any[]>([])

  const discoveryQuestions = [
    {
      id: 'project_name',
      question: 'What is your project or organization called?',
      placeholder: 'e.g., EcoCharge - Solar-Powered EV Stations',
      required: true
    },
    {
      id: 'vision',
      question: 'What is your ultimate vision? What world are you creating?',
      placeholder: 'Paint us a picture of the future you want to see...',
      required: true,
      multiline: true
    },
    {
      id: 'why',
      question: 'Why does this matter to YOU personally? What\'s your story?',
      placeholder: 'This is your passion. Tell us why this keeps you up at night...',
      required: true,
      multiline: true
    },
    {
      id: 'problem',
      question: 'What specific problem are you solving? Who feels this pain TODAY?',
      placeholder: 'Be specific. Real people, real pain...',
      required: true,
      multiline: true
    },
    {
      id: 'solution',
      question: 'How does your solution work? What makes it different?',
      placeholder: 'Explain it like you\'re talking to a friend...',
      required: true,
      multiline: true
    },
    {
      id: 'impact',
      question: 'If you succeed, what changes? How many lives are transformed?',
      placeholder: 'Quantify the impact. Numbers tell stories...',
      required: true,
      multiline: true
    },
    {
      id: 'market',
      question: 'Who are your customers? What market are you in?',
      placeholder: 'Target audience, market size, competitors...',
      required: true,
      multiline: true
    },
    {
      id: 'team',
      question: 'Who\'s on your team? What makes you qualified to win?',
      placeholder: 'Experience, expertise, unique advantages...',
      required: true,
      multiline: true
    },
    {
      id: 'traction',
      question: 'What have you accomplished so far? Any traction, users, revenue?',
      placeholder: 'Prototypes, pilots, customers, partnerships...',
      required: false,
      multiline: true
    },
    {
      id: 'funding_need',
      question: 'How much funding do you need? What will you use it for?',
      placeholder: 'Amount and breakdown (e.g., $500K: 40% tech, 30% team, 30% marketing)...',
      required: true,
      multiline: true
    }
  ]

  const fundingLevels = [
    { id: 'seed', name: 'Seed / Pre-Seed', amount: '$50K - $500K', description: 'Early-stage, MVP, initial traction' },
    { id: 'series_a', name: 'Series A', amount: '$2M - $15M', description: 'Product-market fit, scaling' },
    { id: 'accelerator', name: 'Accelerator (Y-Combinator)', amount: '$125K - $500K', description: 'Program application, demo day pitch' },
    { id: 'enterprise', name: 'Enterprise / Strategic', amount: '$5M+', description: 'Corporate partnerships, B2B sales' },
    { id: 'government', name: 'Government / Grant', amount: 'Varies', description: 'Public sector funding, SBIR/STTR' },
    { id: 'presidential', name: 'Presidential / World Bank', amount: '$50M+', description: 'Nation-scale impact, international funding' }
  ]

  const documentTypes = [
    // Core Documents
    { id: 'exec_summary', name: 'Executive Summary', category: 'core', time: '15 min' },
    { id: 'vision_mission', name: 'Vision & Mission Statement', category: 'core', time: '10 min' },
    { id: 'pitch_deck', name: 'Pitch Deck (15-20 slides)', category: 'core', time: '30 min' },
    { id: 'business_plan', name: 'Business Plan (Full)', category: 'core', time: '45 min' },
    { id: 'one_pager', name: 'One-Pager', category: 'core', time: '10 min' },
    
    // Financial Documents
    { id: 'financial_model', name: 'Financial Model & Projections (3-5 years)', category: 'financial', time: '30 min' },
    { id: 'budget', name: 'Budget Breakdown', category: 'financial', time: '15 min' },
    { id: 'use_of_funds', name: 'Use of Funds Statement', category: 'financial', time: '10 min' },
    { id: 'revenue_model', name: 'Revenue Model Canvas', category: 'financial', time: '20 min' },
    { id: 'cap_table', name: 'Capitalization Table', category: 'financial', time: '15 min' },
    
    // Market & Strategy
    { id: 'market_analysis', name: 'Market Analysis & Research', category: 'market', time: '40 min' },
    { id: 'competitive_analysis', name: 'Competitive Analysis', category: 'market', time: '30 min' },
    { id: 'go_to_market', name: 'Go-to-Market Strategy', category: 'market', time: '25 min' },
    { id: 'customer_personas', name: 'Customer Personas', category: 'market', time: '20 min' },
    
    // Impact & Validation
    { id: 'impact_assessment', name: 'Impact Assessment Report', category: 'impact', time: '35 min' },
    { id: 'case_studies', name: 'Case Studies / Testimonials', category: 'impact', time: '25 min' },
    { id: 'risk_analysis', name: 'Risk Analysis & Mitigation', category: 'impact', time: '20 min' },
    
    // Operations & Governance
    { id: 'org_structure', name: 'Organizational Structure', category: 'operations', time: '15 min' },
    { id: 'hiring_plan', name: 'Hiring Plan & Roadmap', category: 'operations', time: '20 min' },
    { id: 'policies', name: 'Company Policies & Procedures', category: 'operations', time: '30 min' },
    { id: 'governance', name: 'Governance Framework', category: 'operations', time: '25 min' },
    
    // Legal & Compliance
    { id: 'term_sheet', name: 'Term Sheet Template', category: 'legal', time: '20 min' },
    { id: 'data_privacy', name: 'Data Privacy Policy', category: 'legal', time: '20 min' },
    { id: 'ip_strategy', name: 'Intellectual Property Strategy', category: 'legal', time: '25 min' },
    
    // Specialized
    { id: 'demo_day_pitch', name: 'Demo Day Pitch Script', category: 'specialized', time: '15 min' },
    { id: 'investor_memo', name: 'Investor Memo', category: 'specialized', time: '20 min' },
    { id: 'partnership_proposal', name: 'Partnership Proposal', category: 'specialized', time: '25 min' }
  ]

  const handleAnswerChange = (value: string) => {
    const question = discoveryQuestions[currentQuestion]
    setDiscoveryAnswers({ ...discoveryAnswers, [question.id]: value })
  }

  const handleNextQuestion = () => {
    if (currentQuestion < discoveryQuestions.length - 1) {
      setCurrentQuestion(currentQuestion + 1)
    } else {
      setStep('configure')
    }
  }

  const handlePrevQuestion = () => {
    if (currentQuestion > 0) {
      setCurrentQuestion(currentQuestion - 1)
    }
  }

  const toggleDocument = (docId: string) => {
    if (config.selectedDocuments.includes(docId)) {
      setConfig({
        ...config,
        selectedDocuments: config.selectedDocuments.filter(id => id !== docId)
      })
    } else {
      setConfig({
        ...config,
        selectedDocuments: [...config.selectedDocuments, docId]
      })
    }
  }

  const selectAllDocuments = () => {
    setConfig({
      ...config,
      selectedDocuments: documentTypes.map(d => d.id)
    })
  }

  const selectByCategory = (category: string) => {
    const categoryDocs = documentTypes.filter(d => d.category === category).map(d => d.id)
    setConfig({
      ...config,
      selectedDocuments: Array.from(new Set([...config.selectedDocuments, ...categoryDocs]))
    })
  }

  const handleGenerate = async () => {
    setStep('generating')
    setGenerationProgress(0)

    // Simulate document generation with progress
    const totalDocs = config.selectedDocuments.length
    const docs: any[] = []

    for (let i = 0; i < totalDocs; i++) {
      // Simulate API call to backend
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      const docType = documentTypes.find(d => d.id === config.selectedDocuments[i])
      docs.push({
        id: config.selectedDocuments[i],
        name: docType?.name,
        status: 'complete',
        url: '#', // This would be the real download URL from backend
        preview: 'Generated with Outstanding Edition quality...'
      })

      setGenerationProgress(((i + 1) / totalDocs) * 100)
    }

    setGeneratedDocuments(docs)
    setStep('results')
  }

  const getCategoryColor = (category: string) => {
    const colors: any = {
      core: 'from-blue-500 to-blue-600',
      financial: 'from-green-500 to-green-600',
      market: 'from-purple-500 to-purple-600',
      impact: 'from-amber-500 to-amber-600',
      operations: 'from-orange-500 to-orange-600',
      legal: 'from-red-500 to-red-600',
      specialized: 'from-pink-500 to-pink-600'
    }
    return colors[category] || 'from-slate-500 to-slate-600'
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
            <div className="text-xs text-slate-400 uppercase tracking-wider">by Clarity Pearl</div>
          </Link>
          <Link href="/dashboard" className="text-slate-400 hover:text-amber-400 transition-colors">
            ← Back to Dashboard
          </Link>
        </div>
      </header>

      <main className="max-w-7xl mx-auto px-4 py-12">
        {/* Welcome Step */}
        {step === 'welcome' && (
          <div className="max-w-4xl mx-auto text-center">
            <div className="text-6xl mb-6">📄</div>
            <h1 className="text-5xl md:text-6xl font-black mb-6 text-white">
              Funding Readiness Engine
            </h1>
            <p className="text-xl md:text-2xl text-slate-300 mb-8">
              Turn your brilliant idea into <span className="text-amber-400 font-bold">25+ investor-grade documents</span> in under an hour.
            </p>
            <p className="text-lg text-slate-400 mb-12 max-w-2xl mx-auto">
              We'll ask you 10 questions. Then we'll generate everything you need: pitch decks, business plans, financial projections, policies, and more. 
              <span className="text-white font-semibold"> Fortune 50 quality. Y-Combinator standard. Presidential grade.</span>
            </p>

            <div className="grid md:grid-cols-3 gap-6 mb-12">
              <div className="p-6 rounded-xl bg-slate-800/50 border border-white/10">
                <div className="text-3xl mb-3">💬</div>
                <h3 className="text-lg font-bold text-white mb-2">10 Questions</h3>
                <p className="text-slate-400 text-sm">We'll deeply understand your vision, passion, and impact.</p>
              </div>
              <div className="p-6 rounded-xl bg-slate-800/50 border border-white/10">
                <div className="text-3xl mb-3">🤖</div>
                <h3 className="text-lg font-bold text-white mb-2">AI Research</h3>
                <p className="text-slate-400 text-sm">Multi-pass analysis, market research, financial modeling.</p>
              </div>
              <div className="p-6 rounded-xl bg-slate-800/50 border border-white/10">
                <div className="text-3xl mb-3">📦</div>
                <h3 className="text-lg font-bold text-white mb-2">25+ Documents</h3>
                <p className="text-slate-400 text-sm">Download everything. Edit. Present. Get funded.</p>
              </div>
            </div>

            <button
              onClick={() => setStep('discovery')}
              className="px-12 py-5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-900 text-xl font-black rounded-xl transition-all transform hover:scale-105 shadow-2xl"
            >
              Start Your Journey →
            </button>

            <p className="mt-6 text-slate-500 text-sm">Takes ~15 minutes • Outstanding Edition • Human Touch</p>
          </div>
        )}

        {/* Discovery Step */}
        {step === 'discovery' && (
          <div className="max-w-3xl mx-auto">
            {/* Progress Bar */}
            <div className="mb-8">
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-400 text-sm">Question {currentQuestion + 1} of {discoveryQuestions.length}</span>
                <span className="text-slate-400 text-sm">{Math.round(((currentQuestion + 1) / discoveryQuestions.length) * 100)}% complete</span>
              </div>
              <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
                <div 
                  className="h-full bg-gradient-to-r from-amber-500 to-amber-600 transition-all duration-300"
                  style={{ width: `${((currentQuestion + 1) / discoveryQuestions.length) * 100}%` }}
                ></div>
              </div>
            </div>

            {/* Question Card */}
            <div className="p-8 rounded-2xl bg-slate-800/50 border border-white/10 backdrop-blur-xl mb-6">
              <div className="text-5xl mb-6">💭</div>
              <h2 className="text-2xl md:text-3xl font-bold text-white mb-6 leading-relaxed">
                {discoveryQuestions[currentQuestion].question}
              </h2>

              {discoveryQuestions[currentQuestion].multiline ? (
                <textarea
                  value={discoveryAnswers[discoveryQuestions[currentQuestion].id] || ''}
                  onChange={(e) => handleAnswerChange(e.target.value)}
                  placeholder={discoveryQuestions[currentQuestion].placeholder}
                  className="w-full px-6 py-4 bg-slate-900/50 border border-slate-600 rounded-xl text-white placeholder-slate-500 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 transition-all resize-none"
                  rows={6}
                />
              ) : (
                <input
                  type="text"
                  value={discoveryAnswers[discoveryQuestions[currentQuestion].id] || ''}
                  onChange={(e) => handleAnswerChange(e.target.value)}
                  placeholder={discoveryQuestions[currentQuestion].placeholder}
                  className="w-full px-6 py-4 bg-slate-900/50 border border-slate-600 rounded-xl text-white placeholder-slate-500 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 transition-all"
                />
              )}

              {discoveryQuestions[currentQuestion].required && (
                <p className="mt-3 text-amber-400 text-sm">* Required</p>
              )}
            </div>

            {/* Navigation */}
            <div className="flex items-center justify-between">
              <button
                onClick={handlePrevQuestion}
                disabled={currentQuestion === 0}
                className="px-6 py-3 bg-slate-700 hover:bg-slate-600 disabled:bg-slate-800 disabled:text-slate-600 text-white rounded-xl transition-all"
              >
                ← Previous
              </button>

              <button
                onClick={handleNextQuestion}
                disabled={discoveryQuestions[currentQuestion].required && !discoveryAnswers[discoveryQuestions[currentQuestion].id]}
                className="px-8 py-3 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 disabled:from-slate-700 disabled:to-slate-700 disabled:text-slate-500 text-slate-900 font-bold rounded-xl transition-all"
              >
                {currentQuestion === discoveryQuestions.length - 1 ? 'Continue to Documents →' : 'Next →'}
              </button>
            </div>
          </div>
        )}

        {/* Configure Step */}
        {step === 'configure' && (
          <div>
            <div className="text-center mb-12">
              <h1 className="text-4xl md:text-5xl font-black mb-4 text-white">
                Configure Your Funding Package
              </h1>
              <p className="text-xl text-slate-400">
                Select funding level and documents to generate
              </p>
            </div>

            {/* Funding Level Selection */}
            <div className="mb-12">
              <h2 className="text-2xl font-bold text-white mb-6">1. Select Funding Level</h2>
              <div className="grid md:grid-cols-3 gap-4">
                {fundingLevels.map((level) => (
                  <button
                    key={level.id}
                    onClick={() => setConfig({ ...config, fundingLevel: level.id })}
                    className={`p-6 rounded-xl border-2 text-left transition-all ${
                      config.fundingLevel === level.id
                        ? 'border-amber-500 bg-amber-500/10'
                        : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
                    }`}
                  >
                    <h3 className="text-lg font-bold text-white mb-2">{level.name}</h3>
                    <p className="text-amber-400 text-sm mb-2">{level.amount}</p>
                    <p className="text-slate-400 text-sm">{level.description}</p>
                  </button>
                ))}
              </div>
            </div>

            {/* Document Selection */}
            <div className="mb-12">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-white">2. Select Documents to Generate</h2>
                <div className="flex gap-2">
                  <button
                    onClick={selectAllDocuments}
                    className="px-4 py-2 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/30 text-amber-400 rounded-lg text-sm font-semibold transition-all"
                  >
                    Select All ({documentTypes.length})
                  </button>
                  <button
                    onClick={() => setConfig({ ...config, selectedDocuments: [] })}
                    className="px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg text-sm font-semibold transition-all"
                  >
                    Clear
                  </button>
                </div>
              </div>

              {/* Quick Select by Category */}
              <div className="flex flex-wrap gap-2 mb-6">
                {['core', 'financial', 'market', 'impact', 'operations', 'legal', 'specialized'].map((cat) => (
                  <button
                    key={cat}
                    onClick={() => selectByCategory(cat)}
                    className="px-3 py-1 bg-slate-700 hover:bg-slate-600 text-slate-300 rounded-lg text-xs font-semibold uppercase transition-all"
                  >
                    + {cat}
                  </button>
                ))}
              </div>

              {/* Documents Grid */}
              <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                {documentTypes.map((doc) => (
                  <button
                    key={doc.id}
                    onClick={() => toggleDocument(doc.id)}
                    className={`p-4 rounded-xl border-2 text-left transition-all ${
                      config.selectedDocuments.includes(doc.id)
                        ? 'border-green-500 bg-green-500/10'
                        : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
                    }`}
                  >
                    <div className="flex items-start justify-between mb-2">
                      <h3 className="text-white font-semibold text-sm">{doc.name}</h3>
                      <span className={`w-5 h-5 rounded border-2 flex items-center justify-center ${
                        config.selectedDocuments.includes(doc.id)
                          ? 'border-green-500 bg-green-500'
                          : 'border-slate-600'
                      }`}>
                        {config.selectedDocuments.includes(doc.id) && <span className="text-white text-xs">✓</span>}
                      </span>
                    </div>
                    <div className="flex items-center justify-between">
                      <span className={`text-xs px-2 py-1 rounded bg-gradient-to-r ${getCategoryColor(doc.category)} text-white font-semibold uppercase`}>
                        {doc.category}
                      </span>
                      <span className="text-slate-400 text-xs">{doc.time}</span>
                    </div>
                  </button>
                ))}
              </div>

              <div className="mt-6 p-4 rounded-xl bg-blue-500/10 border border-blue-500/30">
                <p className="text-blue-300 text-sm">
                  <span className="font-bold">{config.selectedDocuments.length} documents</span> selected • 
                  Estimated time: <span className="font-bold">
                    {Math.round(config.selectedDocuments.reduce((acc, id) => {
                      const doc = documentTypes.find(d => d.id === id)
                      return acc + parseInt(doc?.time || '0')
                    }, 0) / 60)} - {Math.round(config.selectedDocuments.reduce((acc, id) => {
                      const doc = documentTypes.find(d => d.id === id)
                      return acc + parseInt(doc?.time || '0')
                    }, 0) / 60) + 10} minutes
                  </span>
                </p>
              </div>
            </div>

            {/* Generate Button */}
            <div className="text-center">
              <button
                onClick={handleGenerate}
                disabled={config.selectedDocuments.length === 0}
                className="px-12 py-5 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-400 hover:to-green-500 disabled:from-slate-700 disabled:to-slate-700 disabled:text-slate-500 text-white text-xl font-black rounded-xl transition-all transform hover:scale-105 shadow-2xl"
              >
                Generate {config.selectedDocuments.length} Documents 🚀
              </button>
              <p className="mt-4 text-slate-400 text-sm">Outstanding Edition • Deep Research • Human Touch</p>
            </div>
          </div>
        )}

        {/* Generating Step */}
        {step === 'generating' && (
          <div className="max-w-3xl mx-auto text-center">
            <div className="text-6xl mb-6 animate-pulse">🤖</div>
            <h1 className="text-4xl md:text-5xl font-black mb-6 text-white">
              Generating Your Documents...
            </h1>
            <p className="text-xl text-slate-300 mb-12">
              Our AI is conducting deep research, analyzing markets, and writing with a human touch.
            </p>

            {/* Progress Bar */}
            <div className="mb-8">
              <div className="w-full h-4 bg-slate-700 rounded-full overflow-hidden mb-3">
                <div 
                  className="h-full bg-gradient-to-r from-green-500 to-green-600 transition-all duration-500"
                  style={{ width: `${generationProgress}%` }}
                ></div>
              </div>
              <p className="text-2xl font-bold text-green-400">{Math.round(generationProgress)}%</p>
            </div>

            {/* Status Messages */}
            <div className="space-y-3 text-left">
              {[
                { threshold: 10, message: '🔍 Conducting market research...' },
                { threshold: 25, message: '💡 Analyzing competitive landscape...' },
                { threshold: 40, message: '💰 Building financial models...' },
                { threshold: 55, message: '📊 Generating projections...' },
                { threshold: 70, message: '✍️ Writing with human touch...' },
                { threshold: 85, message: '🎨 Formatting documents...' },
                { threshold: 95, message: '✅ Final quality checks...' }
              ].map((status, i) => (
                generationProgress >= status.threshold && (
                  <div key={i} className="p-3 rounded-lg bg-slate-800/50 border border-slate-700 text-slate-300 animate-fade-in">
                    {status.message}
                  </div>
                )
              ))}
            </div>
          </div>
        )}

        {/* Results Step */}
        {step === 'results' && (
          <div>
            <div className="text-center mb-12">
              <div className="text-6xl mb-6">🎉</div>
              <h1 className="text-4xl md:text-5xl font-black mb-4 text-white">
                Your Funding Package is Ready!
              </h1>
              <p className="text-xl text-slate-400 mb-6">
                {generatedDocuments.length} documents generated with Outstanding Edition quality
              </p>
              <div className="flex flex-wrap gap-3 justify-center">
                <button className="px-6 py-3 bg-green-500 hover:bg-green-400 text-white font-bold rounded-xl transition-all">
                  Download All as ZIP
                </button>
                <button className="px-6 py-3 bg-blue-500 hover:bg-blue-400 text-white font-bold rounded-xl transition-all">
                  Email Package to Me
                </button>
                <button className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white font-bold rounded-xl transition-all">
                  Request Refinement
                </button>
              </div>
            </div>

            {/* Generated Documents List */}
            <div className="grid md:grid-cols-2 gap-4">
              {generatedDocuments.map((doc, i) => (
                <div key={i} className="p-6 rounded-xl bg-slate-800/50 border border-green-500/30 backdrop-blur-xl">
                  <div className="flex items-start justify-between mb-3">
                    <div>
                      <h3 className="text-white font-bold mb-1">{doc.name}</h3>
                      <p className="text-slate-400 text-sm">{doc.preview}</p>
                    </div>
                    <span className="text-green-400 text-2xl">✓</span>
                  </div>
                  <div className="flex gap-2">
                    <button className="flex-1 px-4 py-2 bg-blue-500 hover:bg-blue-400 text-white text-sm font-semibold rounded-lg transition-all">
                      View
                    </button>
                    <button className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white text-sm font-semibold rounded-lg transition-all">
                      Download
                    </button>
                    <button className="px-4 py-2 bg-amber-500/20 hover:bg-amber-500/30 border border-amber-500/30 text-amber-400 text-sm font-semibold rounded-lg transition-all">
                      Refine
                    </button>
                  </div>
                </div>
              ))}
            </div>

            {/* Next Steps */}
            <div className="mt-12 p-8 rounded-2xl bg-gradient-to-br from-amber-500/10 to-green-500/10 border border-amber-500/30">
              <h2 className="text-2xl font-bold text-white mb-4">🚀 Next Steps</h2>
              <ul className="space-y-3 text-slate-300">
                <li className="flex items-start gap-3">
                  <span className="text-green-400 mt-1">✓</span>
                  <span>Review each document and customize with your specific details</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-green-400 mt-1">✓</span>
                  <span>Have your team review and provide feedback (use "Request Refinement")</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-green-400 mt-1">✓</span>
                  <span>Schedule meetings with investors, accelerators, or funding partners</span>
                </li>
                <li className="flex items-start gap-3">
                  <span className="text-green-400 mt-1">✓</span>
                  <span>Update documents as you gain traction and refine your strategy</span>
                </li>
              </ul>
            </div>

            {/* Start Over */}
            <div className="mt-8 text-center">
              <button
                onClick={() => {
                  setStep('welcome')
                  setCurrentQuestion(0)
                  setDiscoveryAnswers({})
                  setConfig({ fundingLevel: 'seed', targetAudience: 'investors', selectedDocuments: [] })
                  setGeneratedDocuments([])
                }}
                className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-xl transition-all"
              >
                Generate Another Package
              </button>
            </div>
          </div>
        )}
      </main>
    </div>
  )
}
