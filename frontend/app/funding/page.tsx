'use client'

import { useState } from 'react'
import Link from 'next/link'

const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'https://veritas-faxh.onrender.com'

type Step = 'welcome' | 'workflow' | 'discovery' | 'documents' | 'gap-questions' | 'configure' | 'generating' | 'results'
type Workflow = 'questions' | 'documents' | null

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
  const [workflow, setWorkflow] = useState<Workflow>(null)
  const [discoveryAnswers, setDiscoveryAnswers] = useState<DiscoveryAnswers>({})
  const [currentQuestion, setCurrentQuestion] = useState(0)
  const [uploadedFiles, setUploadedFiles] = useState<File[]>([])
  const [extractedInfo, setExtractedInfo] = useState<any>(null)
  const [gapQuestions, setGapQuestions] = useState<any[]>([])
  const [isAnalyzing, setIsAnalyzing] = useState(false)
  const [config, setConfig] = useState<DocumentConfig>({
    fundingLevel: 'seed',
    targetAudience: 'investors',
    selectedDocuments: []
  })
  const [generationProgress, setGenerationProgress] = useState(0)
  const [generatedDocuments, setGeneratedDocuments] = useState<any[]>([])
  const [userEmail, setUserEmail] = useState('')
  const [taskId, setTaskId] = useState('')
  const [error, setError] = useState('')
  const [isSubmitting, setIsSubmitting] = useState(false)

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
    // Validate email
    if (!userEmail.trim()) {
      setError('Please enter your email address')
      return
    }
    if (!userEmail.includes('@') || !userEmail.includes('.')) {
      setError('Please enter a valid email address')
      return
    }
    
    setError('')
    setIsSubmitting(true)
    
    try {
      // Call real backend API
      const apiEndpoint = workflow === 'documents' 
        ? `${BACKEND_URL}/v2/funding/generate-from-documents`
        : `${BACKEND_URL}/v2/funding/generate`
      
      // Convert files to base64 if using document workflow
      const documents = workflow === 'documents' && uploadedFiles.length > 0
        ? await Promise.all(uploadedFiles.map(async (file) => {
            const base64 = await fileToBase64(file)
            return {
              filename: file.name,
              content_base64: base64,
              content_type: file.type || 'application/pdf'
            }
          }))
        : undefined

      const response = await fetch(apiEndpoint, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          email: userEmail,
          discovery_answers: discoveryAnswers,
          documents: documents,
          config: {
            ...config,
            formats: ['pdf', 'word', 'pptx'],
            delivery: 'email',
            refine_existing: workflow === 'documents'
          }
        })
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const result = await response.json()
      
      if (result.success) {
        setTaskId(result.task_id)
        
        // Check if questions are needed (document-first workflow)
        if (result.status === 'questions_needed') {
          setExtractedInfo(result.extracted_info)
          setGapQuestions(result.questions)
          setStep('gap-questions')
          setIsSubmitting(false)
          return
        }
        
        setStep('generating')
        setGenerationProgress(0)
        
        // Real progress tracking - poll status endpoint
        const totalDocs = result.generation?.documents_generated || config.selectedDocuments.length
        let progress = 0
        
        // Poll for completion
        const pollInterval = setInterval(async () => {
          try {
            const statusResponse = await fetch(`${BACKEND_URL}/api/funding/status/${result.task_id}`)
            if (statusResponse.ok) {
              const status = await statusResponse.json()
              progress = status.progress || progress + 10
              setGenerationProgress(Math.min(progress, 95))
              
              if (status.status === 'completed' || progress >= 100) {
                clearInterval(pollInterval)
                setGenerationProgress(100)
                
                // Get final documents
                if (result.documents) {
                  setGeneratedDocuments(result.documents.map((doc: any) => ({
                    id: doc.id,
                    name: doc.name,
                    category: doc.category,
                    pages: doc.pages,
                    status: 'complete',
                    refined: doc.refined || false
                  })))
                }
                setStep('results')
              }
            }
          } catch (err) {
            console.error('Status polling error:', err)
          }
        }, 2000)
        
        // Fallback: if no status endpoint, use result data
        if (result.documents) {
          setGeneratedDocuments(result.documents.map((doc: any) => ({
            id: doc.id,
            name: doc.name,
            category: doc.category,
            pages: doc.pages,
            status: 'complete',
            refined: doc.refined || false
          })))
          setGenerationProgress(100)
          setStep('results')
        }
      } else {
        throw new Error(result.error || 'Generation failed')
      }
    } catch (err: any) {
      console.error('Generation error:', err)
      setError(err.message || 'Failed to connect to backend. Please try again.')
      setIsSubmitting(false)
    }
  }

  // Helper function to convert file to base64
  const fileToBase64 = (file: File): Promise<string> => {
    return new Promise((resolve, reject) => {
      const reader = new FileReader()
      reader.onload = () => {
        const base64 = (reader.result as string).split(',')[1]
        resolve(base64)
      }
      reader.onerror = reject
      reader.readAsDataURL(file)
    })
  }

  // Handle document upload and analysis
  const handleDocumentUpload = async (files: FileList | null) => {
    if (!files || files.length === 0) return
    
    const fileArray = Array.from(files)
    setUploadedFiles(fileArray)
    setIsAnalyzing(true)
    setError('')
    
    try {
      // Convert files to base64
      const documents = await Promise.all(fileArray.map(async (file) => {
        const base64 = await fileToBase64(file)
        return {
          filename: file.name,
          content_base64: base64,
          content_type: file.type || 'application/pdf'
        }
      }))
      
      // Analyze documents
      const response = await fetch(`${BACKEND_URL}/v2/funding/analyze-documents`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          documents: documents,
          funding_level: config.fundingLevel
        })
      })
      
      if (!response.ok) {
        throw new Error(`Analysis failed: ${response.status}`)
      }
      
      const result = await response.json()
      
      if (result.success) {
        setExtractedInfo(result.extracted_info)
        setGapQuestions(result.questions)
        setIsAnalyzing(false)
        
        // If there are gaps, go to gap questions step
        if (result.questions && result.questions.length > 0) {
          setStep('gap-questions')
        } else {
          // No gaps, go directly to configure
          setStep('configure')
        }
      } else {
        throw new Error(result.error || 'Document analysis failed')
      }
    } catch (err: any) {
      console.error('Document analysis error:', err)
      setError(err.message || 'Failed to analyze documents')
      setIsAnalyzing(false)
    }
  }

  // Handle gap question answers
  const handleGapAnswer = (field: string, value: string) => {
    setDiscoveryAnswers({ ...discoveryAnswers, [field]: value })
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
          <Link href="/" className="text-slate-400 hover:text-amber-400 transition-colors">
            ← Back to Home
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
              onClick={() => setStep('workflow')}
              className="px-12 py-5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-900 text-xl font-black rounded-xl transition-all transform hover:scale-105 shadow-2xl"
            >
              Start Your Journey →
            </button>

            <p className="mt-6 text-slate-500 text-sm">Takes ~15 minutes • Outstanding Edition • Human Touch</p>
          </div>
        )}

        {/* Workflow Selection Step */}
        {step === 'workflow' && (
          <div className="max-w-4xl mx-auto">
            <div className="text-center mb-12">
              <h1 className="text-4xl md:text-5xl font-black mb-4 text-white">
                Choose Your Path
              </h1>
              <p className="text-xl text-slate-400">
                Start with questions or upload your existing documents
              </p>
            </div>

            <div className="grid md:grid-cols-2 gap-6 mb-8">
              {/* Question-Based Workflow */}
              <button
                onClick={() => {
                  setWorkflow('questions')
                  setStep('discovery')
                }}
                className="p-8 rounded-2xl bg-slate-800/50 border-2 border-slate-700 hover:border-amber-500 transition-all text-left group"
              >
                <div className="text-5xl mb-4">💬</div>
                <h2 className="text-2xl font-bold text-white mb-3">Answer Questions</h2>
                <p className="text-slate-400 mb-4">
                  Perfect if you're starting from scratch. We'll ask you 10 thoughtful questions to understand your vision.
                </p>
                <ul className="text-slate-300 text-sm space-y-2 mb-4">
                  <li>✓ No documents needed</li>
                  <li>✓ Guided discovery process</li>
                  <li>✓ Complete from scratch</li>
                </ul>
                <div className="text-amber-400 font-semibold group-hover:text-amber-300">
                  Start with Questions →
                </div>
              </button>

              {/* Document-First Workflow */}
              <button
                onClick={() => {
                  setWorkflow('documents')
                  setStep('documents')
                }}
                className="p-8 rounded-2xl bg-slate-800/50 border-2 border-slate-700 hover:border-amber-500 transition-all text-left group"
              >
                <div className="text-5xl mb-4">📄</div>
                <h2 className="text-2xl font-bold text-white mb-3">Upload Documents</h2>
                <p className="text-slate-400 mb-4">
                  Already have some documents? Upload them and we'll extract information, then ask only what's missing.
                </p>
                <ul className="text-slate-300 text-sm space-y-2 mb-4">
                  <li>✓ Upload existing docs</li>
                  <li>✓ Smart gap detection</li>
                  <li>✓ Refine or generate new</li>
                </ul>
                <div className="text-amber-400 font-semibold group-hover:text-amber-300">
                  Upload Documents →
                </div>
              </button>
            </div>

            <div className="text-center">
              <button
                onClick={() => setStep('welcome')}
                className="text-slate-400 hover:text-white transition-colors"
              >
                ← Back
              </button>
            </div>
          </div>
        )}

        {/* Document Upload Step */}
        {step === 'documents' && (
          <div className="max-w-3xl mx-auto">
            <div className="text-center mb-8">
              <h1 className="text-4xl md:text-5xl font-black mb-4 text-white">
                Upload Your Documents
              </h1>
              <p className="text-xl text-slate-400">
                Upload pitch decks, business plans, financials, or any funding documents you have
              </p>
            </div>

            <div className="p-8 rounded-2xl bg-slate-800/50 border border-white/10 backdrop-blur-xl mb-6">
              <input
                type="file"
                id="document-upload"
                multiple
                accept=".pdf,.doc,.docx,.txt,.jpg,.jpeg,.png"
                onChange={(e) => handleDocumentUpload(e.target.files)}
                className="hidden"
              />
              <label
                htmlFor="document-upload"
                className="block border-2 border-dashed border-slate-600 rounded-xl p-12 text-center cursor-pointer hover:border-amber-500 transition-all"
              >
                <div className="text-5xl mb-4">📤</div>
                <p className="text-white text-lg font-semibold mb-2">
                  Click to upload or drag and drop
                </p>
                <p className="text-slate-400 text-sm">
                  PDF, Word, Images (PDF, DOCX, JPG, PNG)
                </p>
              </label>

              {uploadedFiles.length > 0 && (
                <div className="mt-6 space-y-2">
                  <p className="text-white font-semibold mb-3">Uploaded Files:</p>
                  {uploadedFiles.map((file, i) => (
                    <div key={i} className="flex items-center justify-between p-3 bg-slate-900/50 rounded-lg">
                      <span className="text-slate-300 text-sm">{file.name}</span>
                      <span className="text-slate-500 text-xs">
                        {(file.size / 1024).toFixed(1)} KB
                      </span>
                    </div>
                  ))}
                </div>
              )}

              {isAnalyzing && (
                <div className="mt-6 p-4 rounded-lg bg-blue-500/10 border border-blue-500/30">
                  <p className="text-blue-300 text-center">
                    🔍 Analyzing documents and extracting information...
                  </p>
                </div>
              )}

              {error && (
                <div className="mt-6 p-4 rounded-lg bg-red-500/10 border border-red-500/30">
                  <p className="text-red-300 text-sm">{error}</p>
                </div>
              )}

              {extractedInfo && !isAnalyzing && (
                <div className="mt-6 p-4 rounded-lg bg-green-500/10 border border-green-500/30">
                  <p className="text-green-300 text-sm mb-2">
                    ✅ Successfully extracted information from {uploadedFiles.length} document(s)
                  </p>
                  {gapQuestions.length > 0 ? (
                    <p className="text-slate-300 text-sm">
                      {gapQuestions.length} question(s) need to be answered to complete.
                    </p>
                  ) : (
                    <p className="text-slate-300 text-sm">
                      All information extracted! Ready to generate documents.
                    </p>
                  )}
                </div>
              )}
            </div>

            <div className="flex items-center justify-between">
              <button
                onClick={() => setStep('workflow')}
                className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-xl transition-all"
              >
                ← Back
              </button>

              {extractedInfo && (
                <button
                  onClick={() => {
                    if (gapQuestions.length > 0) {
                      setStep('gap-questions')
                    } else {
                      setStep('configure')
                    }
                  }}
                  className="px-8 py-3 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-900 font-bold rounded-xl transition-all"
                >
                  Continue →
                </button>
              )}
            </div>
          </div>
        )}

        {/* Gap Questions Step */}
        {step === 'gap-questions' && (
          <div className="max-w-3xl mx-auto">
            <div className="mb-8">
              <div className="flex items-center justify-between mb-2">
                <span className="text-slate-400 text-sm">
                  Question {currentQuestion + 1} of {gapQuestions.length}
                </span>
                <span className="text-slate-400 text-sm">
                  {Math.round(((currentQuestion + 1) / gapQuestions.length) * 100)}% complete
                </span>
              </div>
              <div className="w-full h-2 bg-slate-700 rounded-full overflow-hidden">
                <div
                  className="h-full bg-gradient-to-r from-amber-500 to-amber-600 transition-all duration-300"
                  style={{ width: `${((currentQuestion + 1) / gapQuestions.length) * 100}%` }}
                ></div>
              </div>
            </div>

            <div className="p-8 rounded-2xl bg-slate-800/50 border border-white/10 backdrop-blur-xl mb-6">
              <div className="text-5xl mb-6">❓</div>
              <div className="mb-4">
                <span className={`px-3 py-1 rounded-full text-xs font-semibold ${
                  gapQuestions[currentQuestion]?.priority === 'high'
                    ? 'bg-red-500/20 text-red-300'
                    : gapQuestions[currentQuestion]?.priority === 'medium'
                    ? 'bg-yellow-500/20 text-yellow-300'
                    : 'bg-blue-500/20 text-blue-300'
                }`}>
                  {gapQuestions[currentQuestion]?.priority?.toUpperCase()} PRIORITY
                </span>
              </div>
              <h2 className="text-2xl md:text-3xl font-bold text-white mb-4 leading-relaxed">
                {gapQuestions[currentQuestion]?.question}
              </h2>
              {gapQuestions[currentQuestion]?.why_important && (
                <p className="text-slate-400 text-sm mb-6">
                  💡 {gapQuestions[currentQuestion].why_important}
                </p>
              )}

              <textarea
                value={discoveryAnswers[gapQuestions[currentQuestion]?.field] || ''}
                onChange={(e) => handleGapAnswer(gapQuestions[currentQuestion]?.field, e.target.value)}
                placeholder="Type your answer here..."
                className="w-full px-6 py-4 bg-slate-900/50 border border-slate-600 rounded-xl text-white placeholder-slate-500 focus:border-amber-500 focus:ring-2 focus:ring-amber-500/20 transition-all resize-none"
                rows={6}
              />
            </div>

            <div className="flex items-center justify-between">
              <button
                onClick={() => {
                  if (currentQuestion > 0) {
                    setCurrentQuestion(currentQuestion - 1)
                  } else {
                    setStep('documents')
                  }
                }}
                className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-xl transition-all"
              >
                ← Previous
              </button>

              <button
                onClick={() => {
                  if (currentQuestion < gapQuestions.length - 1) {
                    setCurrentQuestion(currentQuestion + 1)
                  } else {
                    setStep('configure')
                  }
                }}
                disabled={!discoveryAnswers[gapQuestions[currentQuestion]?.field]}
                className="px-8 py-3 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 disabled:from-slate-700 disabled:to-slate-700 disabled:text-slate-500 text-slate-900 font-bold rounded-xl transition-all"
              >
                {currentQuestion === gapQuestions.length - 1 ? 'Continue to Documents →' : 'Next →'}
              </button>
            </div>
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

            {/* Email Collection */}
            <div className="mb-8">
              <label className="block text-white font-bold mb-3 text-lg">Where should we send your documents?</label>
              <input
                type="email"
                value={userEmail}
                onChange={(e) => setUserEmail(e.target.value)}
                placeholder="your.email@company.com"
                className="w-full px-6 py-4 bg-slate-800 border-2 border-slate-700 focus:border-amber-500 rounded-xl text-white text-lg transition-all focus:outline-none"
              />
              {error && (
                <p className="mt-2 text-red-400 text-sm flex items-center gap-2">
                  <span>⚠️</span>
                  <span>{error}</span>
                </p>
              )}
              <p className="mt-2 text-slate-400 text-sm">
                📧 Your funding package will be emailed to this address when ready (5-15 minutes)
              </p>
            </div>

            {/* Generate Button */}
            <div className="text-center">
              <button
                onClick={handleGenerate}
                disabled={config.selectedDocuments.length === 0 || isSubmitting}
                className="px-12 py-5 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-400 hover:to-green-500 disabled:from-slate-700 disabled:to-slate-700 disabled:text-slate-500 text-white text-xl font-black rounded-xl transition-all transform hover:scale-105 shadow-2xl"
              >
                {isSubmitting ? 'Submitting...' : `Generate ${config.selectedDocuments.length} Documents 🚀`}
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
              <p className="text-xl text-slate-400 mb-2">
                {generatedDocuments.length} documents generated with Outstanding Edition quality
              </p>
              <p className="text-lg text-green-400 mb-6">
                📧 Check your email: <span className="font-bold">{userEmail}</span>
              </p>
              <div className="p-6 rounded-xl bg-green-500/10 border border-green-500/30 mb-6">
                <p className="text-green-300 text-center">
                  <span className="font-bold">✅ Success!</span> Your funding package has been generated and will be emailed to <span className="font-bold">{userEmail}</span> within 5-15 minutes.
                </p>
                <p className="text-green-400 text-sm text-center mt-2">
                  Task ID: <code className="bg-slate-900/50 px-2 py-1 rounded">{taskId}</code>
                </p>
              </div>
              <div className="flex flex-wrap gap-3 justify-center">
                <a
                  href={`${BACKEND_URL}/api/funding/download/${taskId}`}
                  className="px-6 py-3 bg-green-500 hover:bg-green-400 text-white font-bold rounded-xl transition-all"
                >
                  Download All as ZIP
                </a>
                <button 
                  onClick={async () => {
                    try {
                      const response = await fetch(`${BACKEND_URL}/api/funding/resend-email`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ task_id: taskId, email: userEmail })
                      })
                      if (response.ok) {
                        alert('Email resent successfully!')
                      } else {
                        alert('Email resend failed. Please check your email inbox.')
                      }
                    } catch (err) {
                      alert('Email already sent. Please check your inbox.')
                    }
                  }}
                  className="px-6 py-3 bg-blue-500 hover:bg-blue-400 text-white font-bold rounded-xl transition-all"
                >
                  Resend Email
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
                    <a
                      href={`${BACKEND_URL}/api/funding/document/${doc.id}/${taskId}`}
                      target="_blank"
                      className="flex-1 px-4 py-2 bg-blue-500 hover:bg-blue-400 text-white text-sm font-semibold rounded-lg transition-all text-center"
                    >
                      View
                    </a>
                    <a
                      href={`${BACKEND_URL}/api/funding/download/${taskId}/${doc.id}`}
                      className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white text-sm font-semibold rounded-lg transition-all text-center"
                    >
                      Download
                    </a>
                    {doc.refined && (
                      <span className="px-4 py-2 bg-green-500/20 border border-green-500/30 text-green-400 text-sm font-semibold rounded-lg">
                        ✨ Refined
                      </span>
                    )}
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
