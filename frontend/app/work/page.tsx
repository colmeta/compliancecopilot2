'use client'

import { useState, Suspense } from 'react'
import Link from 'next/link'
import { useSearchParams } from 'next/navigation'

// Backend API URL
const BACKEND_URL = process.env.NEXT_PUBLIC_API_URL || 'https://veritas-faxh.onrender.com'

type Mode = 'ask' | 'plan' | 'agent'

function CommandDeckContent() {
  const searchParams = useSearchParams()
  const initialDomain = searchParams?.get('domain') || 'legal'
  
  const [mode, setMode] = useState<Mode>('ask')
  const [selectedDomain, setSelectedDomain] = useState(initialDomain)
  const [directive, setDirective] = useState('')
  const [files, setFiles] = useState<File[]>([])
  const [submitted, setSubmitted] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [taskId, setTaskId] = useState('')
  const [analysis, setAnalysis] = useState<any>(null)
  const [plan, setPlan] = useState<any>(null)
  const [planApproved, setPlanApproved] = useState(false)
  const [executing, setExecuting] = useState(false)
  const [executionResults, setExecutionResults] = useState<any[]>([])
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
    
    // Track response time for error detection
    let responseTime: number | null = null
    const startTime = Date.now()
    
    try {
      if (mode === 'ask') {
        // Ask mode: Direct execution
        // Track response time to detect hibernation (slow = hibernating, fast = awake)
        const controller = new AbortController()
        // Longer timeout for document processing (60 seconds if files, 30 if not)
        const timeout = files.length > 0 ? 60000 : 30000
        const timeoutId = setTimeout(() => controller.abort(), timeout)
        
        // Prepare request body with files if uploaded
        let requestBody: any = {
          directive: directive,
          domain: selectedDomain
        }
        
        // If files are uploaded, convert to base64 and add to request
        if (files.length > 0) {
          const filesData = await Promise.all(files.map(async (file) => {
            const base64 = await new Promise<string>((resolve, reject) => {
              const reader = new FileReader()
              reader.onload = () => {
                const result = reader.result as string
                const base64Content = result.split(',')[1] // Remove data:type;base64, prefix
                resolve(base64Content)
              }
              reader.onerror = reject
              reader.readAsDataURL(file)
            })
            
            return {
              filename: file.name,
              content_base64: base64,
              content_type: file.type || 'application/pdf'
            }
          }))
          
          requestBody.files = filesData
        }
        
        const response = await fetch(`${BACKEND_URL}/real/analyze`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify(requestBody),
          signal: controller.signal
        })
        
        clearTimeout(timeoutId)
        responseTime = Date.now() - startTime

        if (!response.ok) {
          // If response was fast (< 5 seconds), backend is awake but has an error
          if (responseTime < 5000) {
            throw new Error(`API error: ${response.status} - Backend is awake but returned an error`)
          } else {
            // Slow response might indicate hibernation, but we got a response so it's an API error
            throw new Error(`API error: ${response.status}`)
          }
        }

        const result = await response.json()
        
        console.log('Backend response:', result) // Debug log
        
        if (result.success) {
          setTaskId(result.task_id || result.taskId || '')
          // Handle different response formats
          if (result.analysis) {
            setAnalysis(result.analysis)
          } else if (result.data) {
            setAnalysis(result.data)
          } else {
            // If no analysis field, use the whole result
            setAnalysis(result)
          }
          setSubmitted(true)
        } else {
          // Backend responded with an error - show the actual error message
          const backendError = result.error || result.message || 'Analysis failed'
          throw new Error(`Backend error: ${backendError}`)
        }
      } else if (mode === 'plan') {
        // Plan mode: Create plan first
        const controller = new AbortController()
        const timeoutId = setTimeout(() => controller.abort(), 30000)
        
        const response = await fetch(`${BACKEND_URL}/api/planning/create-plan`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            task_description: directive,
            task_type: 'analysis',
            domain: selectedDomain,
            context: {
              files: files.length > 0 ? files.map(f => f.name) : [],
              user_tier: 'free'
            }
          }),
          signal: controller.signal
        })
        
        clearTimeout(timeoutId)

        if (!response.ok) {
          throw new Error(`API error: ${response.status}`)
        }

        const result = await response.json()
        
        if (result.success) {
          setPlan(result.plan)
          setSubmitted(true)
        } else {
          throw new Error(result.error || 'Plan creation failed')
        }
      } else if (mode === 'agent') {
        // Agent mode: Create plan and execute automatically
        // First create plan
        const controller1 = new AbortController()
        const timeoutId1 = setTimeout(() => controller1.abort(), 30000)
        
        const planResponse = await fetch(`${BACKEND_URL}/api/planning/create-plan`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            task_description: directive,
            task_type: 'analysis',
            domain: selectedDomain,
            context: {
              files: files.length > 0 ? files.map(f => f.name) : [],
              user_tier: 'free'
            }
          }),
          signal: controller1.signal
        })
        
        clearTimeout(timeoutId1)

        if (!planResponse.ok) {
          throw new Error(`Plan creation failed: ${planResponse.status}`)
        }

        const planResult = await planResponse.json()
        
        if (!planResult.success) {
          throw new Error(planResult.error || 'Plan creation failed')
        }

        setPlan(planResult.plan)
        setPlanApproved(true)
        setExecuting(true)

        // Auto-approve and execute
        const controller2 = new AbortController()
        const timeoutId2 = setTimeout(() => controller2.abort(), 60000) // Longer timeout for execution
        
        const executeResponse = await fetch(`${BACKEND_URL}/api/planning/execute-plan`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            plan: planResult.plan,
            mode: 'agent',
            auto_approve: true,
            context: {
              directive: directive,
              domain: selectedDomain
            }
          }),
          signal: controller2.signal
        })
        
        clearTimeout(timeoutId2)

        if (!executeResponse.ok) {
          throw new Error(`Execution failed: ${executeResponse.status}`)
        }

        const executeResult = await executeResponse.json()
        
        if (executeResult.success) {
          setPlan(executeResult.plan)
          setExecutionResults(executeResult.execution_results || [])
          setExecuting(false)
          setSubmitted(true)
          
          // Also get analysis result (would come from execution)
          if (executeResult.analysis) {
            setAnalysis(executeResult.analysis)
          }
        } else {
          throw new Error(executeResult.error || 'Execution failed')
        }
      }
    } catch (err: any) {
      console.error('Error:', err)
      
      // Detect specific error types - only show hibernation for actual timeouts/network failures
      let errorMessage = err.message || 'Failed to connect to backend'
      let isHibernation = false
      
      // Check if we got a response from backend (means it's awake)
      if (err.message?.includes('Backend error:')) {
        // Backend responded with an error - NOT hibernation, show actual error
        isHibernation = false
        errorMessage = err.message.replace('Backend error: ', '')
      } else if (err.message?.includes('API error:')) {
        // HTTP error response - backend is awake
        isHibernation = false
        // Extract status code if available
        const statusMatch = err.message.match(/API error: (\d+)/)
        if (statusMatch) {
          const status = statusMatch[1]
          if (status === '400') {
            errorMessage = 'Invalid request. Please check your input and try again.'
          } else if (status === '401' || status === '403') {
            errorMessage = 'Authentication error. Please check your API key.'
          } else if (status === '404') {
            errorMessage = 'Endpoint not found. Please check the API URL.'
          } else if (status === '500') {
            errorMessage = 'Server error. The backend encountered an issue. Please try again.'
          } else {
            errorMessage = `Server returned error ${status}. Please try again.`
          }
        } else {
          errorMessage = err.message.replace('API error: ', '')
        }
      } else if (err.name === 'AbortError') {
        // Request timed out - check if it's hibernation or just slow processing
        if (files.length > 0) {
          // Document processing can take time - not necessarily hibernation
          isHibernation = false
          errorMessage = 'Document processing timed out. The file may be too large or the backend is processing. Please try again or use a smaller file.'
        } else {
          // No files - timeout likely means hibernation
          isHibernation = true
          errorMessage = 'Backend is waking up (took too long to respond). Please wait 30-60 seconds and try again.'
        }
      } else if (err.message?.includes('Failed to fetch')) {
        // Network error - try to determine the actual cause
        // First, check if we got any response at all
        if (responseTime === null) {
          // No response received - could be CORS, network, or hibernation
          // Since backend is confirmed awake, it's likely CORS or network issue
          isHibernation = false
          errorMessage = 'Failed to connect to backend. This might be a CORS issue or network problem. Please check the browser console (F12) for details.'
        } else if (responseTime > 25000) {
          // Very slow - likely hibernation
          isHibernation = true
          errorMessage = 'Backend is waking up (connection failed). Please wait 30-60 seconds and try again.'
        } else {
          // Fast failure - connection issue, not hibernation
          isHibernation = false
          errorMessage = 'Connection failed. Please check your internet connection and try again. If this persists, check browser console (F12) for CORS errors.'
        }
      } else {
        // Any other error - backend is awake, just has an issue
        isHibernation = false
        // Keep the original error message
      }
      
      setError(errorMessage)
      
      // Only show hibernation-specific alert for actual hibernation
      if (isHibernation) {
        alert(`Backend is waking up...\n\nRender free tier services hibernate after 15 minutes of inactivity.\n\nPlease wait 30-60 seconds and try again.\n\n💡 Tip: The keep-alive service should prevent this. Check GitHub Actions if it persists.`)
      } else {
        alert(`Error: ${errorMessage}\n\nPlease check your connection and try again.`)
      }
      
      setExecuting(false)
    } finally {
      setSubmitting(false)
    }
  }

  const handleApprovePlan = async () => {
    if (!plan) return

    setSubmitting(true)
    setError('')
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/planning/approve-plan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          plan: plan,
          plan_id: plan.plan_id
        })
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const result = await response.json()
      
      if (result.success) {
        setPlan(result.plan)
        setPlanApproved(true)
      } else {
        throw new Error(result.error || 'Plan approval failed')
      }
    } catch (err: any) {
      console.error('Approval error:', err)
      setError(err.message || 'Failed to approve plan')
      alert(`Error: ${err.message}. Please try again.`)
    } finally {
      setSubmitting(false)
    }
  }

  const handleExecutePlan = async () => {
    if (!plan || !planApproved) return

    setExecuting(true)
    setError('')
    
    try {
      const response = await fetch(`${BACKEND_URL}/api/planning/execute-plan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          plan: plan,
          mode: 'manual',
          auto_approve: false,
          context: {
            directive: directive,
            domain: selectedDomain
          }
        })
      })

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`)
      }

      const result = await response.json()
      
      if (result.success) {
        setPlan(result.plan)
        setExecutionResults(result.execution_results || [])
        setExecuting(false)
        
        // Get analysis result
        if (result.analysis) {
          setAnalysis(result.analysis)
        }
      } else {
        throw new Error(result.error || 'Execution failed')
      }
    } catch (err: any) {
      console.error('Execution error:', err)
      setError(err.message || 'Failed to execute plan')
      setExecuting(false)
    }
  }

  // Show plan review if in plan mode and plan exists but not approved
  if (submitted && mode === 'plan' && plan && !planApproved) {
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
          <div className="text-center mb-12">
            <div className="text-6xl mb-6">📋</div>
            <h1 className="text-4xl md:text-5xl font-black mb-4 text-white">
              Execution Plan Created
            </h1>
            <p className="text-xl text-slate-300">
              Review the plan before execution
            </p>
          </div>

          <div className="bg-slate-800/50 rounded-2xl p-8 border border-white/10 backdrop-blur-xl mb-8">
            <div className="mb-6">
              <h2 className="text-2xl font-bold text-white mb-2">Approach</h2>
              <p className="text-slate-300">{plan.approach}</p>
            </div>

            <div className="mb-6">
              <h2 className="text-2xl font-bold text-white mb-4">Execution Steps</h2>
              <div className="space-y-4">
                {plan.steps?.map((step: any, index: number) => (
                  <div key={index} className="p-4 rounded-lg bg-slate-900/50 border border-slate-700">
                    <div className="flex items-start gap-4">
                      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-blue-500/20 border border-blue-500/30 flex items-center justify-center text-blue-300 font-bold">
                        {step.step_number}
                      </div>
                      <div className="flex-1">
                        <h3 className="text-white font-bold mb-1">{step.title}</h3>
                        <p className="text-slate-400 text-sm mb-2">{step.description}</p>
                        <p className="text-slate-500 text-xs italic">Why: {step.rationale}</p>
                        <div className="mt-2 flex items-center gap-4 text-xs text-slate-500">
                          <span>⏱️ {step.estimated_time} min</span>
                          {step.dependencies && step.dependencies.length > 0 && (
                            <span>Depends on: {step.dependencies.join(', ')}</span>
                          )}
                        </div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="p-4 rounded-lg bg-blue-500/10 border border-blue-500/30 mb-6">
              <p className="text-blue-300 text-sm">
                <strong>Total Estimated Time:</strong> {plan.total_estimated_time} minutes
              </p>
            </div>

            <div className="flex gap-4">
              <button
                onClick={() => {
                  setSubmitted(false)
                  setPlan(null)
                }}
                className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white font-bold rounded-xl transition-all"
              >
                ← Back to Edit
              </button>
              <button
                onClick={handleApprovePlan}
                disabled={submitting}
                className="flex-1 px-8 py-3 bg-gradient-to-r from-green-500 to-green-600 hover:from-green-600 hover:to-green-700 disabled:from-slate-700 disabled:to-slate-700 text-white font-bold rounded-xl transition-all"
              >
                {submitting ? 'Approving...' : '✓ Approve & Execute Plan'}
              </button>
            </div>
          </div>
        </main>
      </div>
    )
  }

  // Show execution progress if executing
  if (executing && mode === 'agent') {
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
          <div className="text-center mb-12">
            <div className="text-6xl mb-6 animate-pulse">🤖</div>
            <h1 className="text-4xl md:text-5xl font-black mb-4 text-white">
              Agent Executing Plan
            </h1>
            <p className="text-xl text-slate-300">
              Autonomous execution in progress...
            </p>
          </div>

          {plan && (
            <div className="bg-slate-800/50 rounded-2xl p-8 border border-white/10 backdrop-blur-xl mb-8">
              <div className="mb-6">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-slate-400">Progress</span>
                  <span className="text-white font-bold">
                    {plan.completed_steps || 0} / {plan.total_steps || plan.steps?.length || 0} steps
                  </span>
                </div>
                <div className="w-full h-3 bg-slate-700 rounded-full overflow-hidden">
                  <div
                    className="h-full bg-gradient-to-r from-green-500 to-green-600 transition-all duration-500"
                    style={{
                      width: `${((plan.completed_steps || 0) / (plan.total_steps || plan.steps?.length || 1)) * 100}%`
                    }}
                  />
                </div>
              </div>

              <div className="space-y-3">
                {plan.steps?.map((step: any, index: number) => (
                  <div
                    key={index}
                    className={`p-4 rounded-lg border ${
                      step.status === 'completed'
                        ? 'bg-green-500/10 border-green-500/30'
                        : step.status === 'in_progress'
                        ? 'bg-blue-500/10 border-blue-500/30 animate-pulse'
                        : 'bg-slate-900/50 border-slate-700'
                    }`}
                  >
                    <div className="flex items-center gap-3">
                      <span className="text-2xl">
                        {step.status === 'completed' ? '✓' : step.status === 'in_progress' ? '⟳' : '○'}
                      </span>
                      <span className={`font-semibold ${
                        step.status === 'completed' ? 'text-green-300' : step.status === 'in_progress' ? 'text-blue-300' : 'text-slate-400'
                      }`}>
                        {step.title}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </div>
          )}
        </main>
      </div>
    )
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
              <span className="text-amber-400 font-bold">{currentDomain.name}</span> analysis complete
            </p>
          </div>

          {/* Analysis Results */}
          {analysis ? (
            <div className="bg-slate-800/50 rounded-2xl p-8 border border-white/10 backdrop-blur-xl mb-8">
              {/* Header */}
              <div className="flex items-start justify-between mb-6 pb-6 border-b border-white/10">
                <div className="flex-1">
                  <h2 className="text-3xl font-bold text-white mb-3">
                    {analysis.summary || analysis.domain || 'Analysis Results'}
                  </h2>
                  {analysis.confidence && (
                    <div className="flex items-center gap-4">
                      <span className="text-slate-400">Confidence Score:</span>
                      <span className="text-green-400 font-bold text-xl">{Math.round((analysis.confidence || 0) * 100)}%</span>
                      <div className="flex-1 max-w-xs h-2 bg-slate-700 rounded-full overflow-hidden">
                        <div 
                          className="h-full bg-green-500 rounded-full transition-all duration-500"
                          style={{ width: `${(analysis.confidence || 0) * 100}%` }}
                        />
                      </div>
                    </div>
                  )}
                </div>
              </div>

              {/* Findings */}
              {analysis.findings && analysis.findings.length > 0 && (
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
              )}

              {/* Recommendations */}
              {analysis.recommendations && analysis.recommendations.length > 0 && (
                <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-6 mb-8">
                  <h3 className="text-lg font-bold text-blue-300 mb-2 flex items-center gap-2">
                    <span>📋</span> Recommendations
                  </h3>
                  <ul className="space-y-2">
                    {analysis.recommendations.map((rec: string, index: number) => (
                      <li key={index} className="text-slate-300 flex items-start gap-2">
                        <span className="text-blue-400">•</span>
                        <span>{rec}</span>
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Next Steps (if exists) */}
              {analysis.next_steps && (
                <div className="bg-blue-500/10 border border-blue-500/20 rounded-xl p-6 mb-8">
                  <h3 className="text-lg font-bold text-blue-300 mb-2 flex items-center gap-2">
                    <span>📋</span> Recommended Next Steps
                  </h3>
                  <p className="text-slate-300">{analysis.next_steps}</p>
                </div>
              )}

              {/* Raw Analysis (if structured data not available) */}
              {(!analysis.findings || analysis.findings.length === 0) && 
               (!analysis.recommendations || analysis.recommendations.length === 0) && 
               (analysis.raw_response || typeof analysis === 'string') && (
                <div className="bg-slate-900/50 rounded-xl p-6 mb-8">
                  <h3 className="text-lg font-bold text-white mb-4">Analysis Results</h3>
                  <div className="text-slate-300 whitespace-pre-wrap">
                    {analysis.raw_response || (typeof analysis === 'string' ? analysis : JSON.stringify(analysis, null, 2))}
                  </div>
                </div>
              )}

              {/* Debug: Show full analysis object if nothing else displays */}
              {(!analysis.summary || analysis.summary.length < 10) && 
               (!analysis.findings || analysis.findings.length === 0) && 
               (!analysis.recommendations || analysis.recommendations.length === 0) && 
               !analysis.raw_response && (
                <div className="bg-yellow-500/10 border border-yellow-500/20 rounded-xl p-6 mb-8">
                  <h3 className="text-lg font-bold text-yellow-300 mb-2">Analysis Received</h3>
                  <p className="text-slate-300 mb-4">The analysis completed but the response format was unexpected. Showing raw data:</p>
                  <pre className="text-xs text-slate-400 bg-slate-900/50 p-4 rounded overflow-auto max-h-96">
                    {JSON.stringify(analysis, null, 2)}
                  </pre>
                </div>
              )}
            </div>
          ) : (
            <div className="bg-slate-800/50 rounded-2xl p-8 border border-white/10 backdrop-blur-xl mb-8">
              <div className="text-center py-12">
                <div className="text-6xl mb-4">⚠️</div>
                <h3 className="text-2xl font-bold text-white mb-2">No Analysis Data</h3>
                <p className="text-slate-400">The analysis completed but no results were returned. Please check the backend logs.</p>
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

              {/* Mode Selector */}
              <div className="mb-8">
                <label className="block text-white font-bold mb-4 text-lg">
                  Choose Your Mode
                </label>
                <div className="grid md:grid-cols-3 gap-4">
                  <button
                    onClick={() => setMode('ask')}
                    className={`p-6 rounded-xl border-2 transition-all text-left ${
                      mode === 'ask'
                        ? 'border-amber-500 bg-amber-500/10'
                        : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
                    }`}
                  >
                    <div className="text-3xl mb-2">💬</div>
                    <h3 className="text-white font-bold mb-1">Ask</h3>
                    <p className="text-slate-400 text-sm">
                      Direct execution. Get instant results.
                    </p>
                  </button>
                  
                  <button
                    onClick={() => setMode('plan')}
                    className={`p-6 rounded-xl border-2 transition-all text-left ${
                      mode === 'plan'
                        ? 'border-blue-500 bg-blue-500/10'
                        : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
                    }`}
                  >
                    <div className="text-3xl mb-2">📋</div>
                    <h3 className="text-white font-bold mb-1">Plan</h3>
                    <p className="text-slate-400 text-sm">
                      Review plan first, then execute.
                    </p>
                  </button>
                  
                  <button
                    onClick={() => setMode('agent')}
                    className={`p-6 rounded-xl border-2 transition-all text-left ${
                      mode === 'agent'
                        ? 'border-green-500 bg-green-500/10'
                        : 'border-slate-700 bg-slate-800/50 hover:border-slate-600'
                    }`}
                  >
                    <div className="text-3xl mb-2">🤖</div>
                    <h3 className="text-white font-bold mb-1">Agent</h3>
                    <p className="text-slate-400 text-sm">
                      Autonomous execution with plan.
                    </p>
                  </button>
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
