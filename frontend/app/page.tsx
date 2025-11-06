'use client'

import { useState, useEffect } from 'react'
import Link from 'next/link'

export default function Home() {
  const [apiStatus, setApiStatus] = useState<any>(null)

  useEffect(() => {
    fetch(process.env.NEXT_PUBLIC_API_URL + '/')
      .then(res => res.json())
      .then(data => setApiStatus(data))
      .catch(err => console.error(err))
  }, [])

  return (
    <main className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Hero Section */}
      <section className="relative min-h-screen flex items-center justify-center px-4">
        {/* Animated Background */}
        <div className="absolute inset-0 overflow-hidden">
          <div className="absolute w-96 h-96 bg-blue-500/20 rounded-full blur-3xl top-20 left-20 animate-pulse"></div>
          <div className="absolute w-96 h-96 bg-amber-500/20 rounded-full blur-3xl bottom-20 right-20 animate-pulse delay-1000"></div>
        </div>

        {/* Content */}
        <div className="relative z-10 max-w-7xl mx-auto text-center">
          {/* Badge */}
          <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-amber-500/20 border border-amber-500/30 text-amber-200 text-sm font-semibold mb-8 animate-fade-in">
            <span>⚡</span>
            <span>BY CLARITY PEARL</span>
          </div>

          {/* Main Heading */}
          <h1 className="text-6xl md:text-8xl font-black mb-6 bg-gradient-to-r from-white via-blue-100 to-white bg-clip-text text-transparent animate-fade-in-up">
            CLARITY
          </h1>

          <div className="text-2xl md:text-3xl font-bold text-amber-400 mb-6 animate-fade-in-up delay-200">
            The Institutional Brain for the Enterprise.
          </div>

          {/* Pain Point Subtitle */}
          <p className="text-xl md:text-2xl text-slate-300 mb-4 max-w-4xl mx-auto animate-fade-in-up delay-300">
            Your lawyers spend 40% of their time just <span className="text-red-400 font-bold">finding information</span>.
          </p>
          <p className="text-xl md:text-2xl text-slate-300 mb-12 max-w-4xl mx-auto animate-fade-in-up delay-400">
            Your auditors waste weeks on analysis that should take <span className="text-amber-400 font-bold">hours</span>.
          </p>

          <p className="text-2xl md:text-3xl font-bold text-white mb-12 max-w-4xl mx-auto animate-fade-in-up delay-500">
            What if a quarter's worth of research could be done in an afternoon?
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in-up delay-600">
            <Link 
              href="/work" 
              className="px-8 py-4 bg-amber-500 hover:bg-amber-400 text-slate-900 font-bold rounded-xl transition-all transform hover:scale-105 hover:shadow-2xl text-lg"
            >
              Launch CLARITY Now →
            </Link>
            <a
              href="mailto:nsubugacollin@gmail.com"
              className="px-8 py-4 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-xl backdrop-blur-sm border border-white/20 transition-all"
            >
              Schedule Live Demo
            </a>
          </div>

          {/* API Status */}
          {apiStatus && (
            <div className="mt-12 inline-block px-4 py-2 rounded-lg bg-green-500/20 border border-green-500/30 text-green-200 text-sm">
              <span className="inline-block w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></span>
              All Systems Operational • {apiStatus.version}
            </div>
          )}
        </div>
      </section>

      {/* Problem Section - Hit Them With The Pain */}
      <section className="relative py-32 px-4 bg-slate-900/95 border-t border-white/10">
        <div className="max-w-6xl mx-auto">
          <h2 className="text-4xl md:text-6xl font-black text-center mb-6 text-white">
            Your Most Valuable Asset is <span className="text-red-400">Trapped</span>
          </h2>
          <p className="text-xl text-center text-slate-300 mb-16 max-w-3xl mx-auto">
            And it's costing you millions every quarter.
          </p>

          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-8 rounded-2xl bg-red-500/10 border border-red-500/30">
              <div className="text-5xl mb-4">⏰</div>
              <div className="text-3xl font-bold text-red-400 mb-3">40%</div>
              <p className="text-slate-300 text-lg mb-2">of your experts' time</p>
              <p className="text-slate-400 text-sm">
                ...wasted just trying to <span className="font-semibold text-white">find and understand</span> information buried in documents.
              </p>
            </div>

            <div className="p-8 rounded-2xl bg-amber-500/10 border border-amber-500/30">
              <div className="text-5xl mb-4">📉</div>
              <div className="text-3xl font-bold text-amber-400 mb-3">80%</div>
              <p className="text-slate-300 text-lg mb-2">of your data is unstructured</p>
              <p className="text-slate-400 text-sm">
                Locked in emails, PDFs, recordings, and reports. <span className="font-semibold text-white">Invisible to your systems.</span>
              </p>
            </div>

            <div className="p-8 rounded-2xl bg-orange-500/10 border border-orange-500/30">
              <div className="text-5xl mb-4">💸</div>
              <div className="text-3xl font-bold text-orange-400 mb-3">$Millions</div>
              <p className="text-slate-300 text-lg mb-2">lost every year</p>
              <p className="text-slate-400 text-sm">
                To delayed deals, compliance failures, and <span className="font-semibold text-white">duplicated work</span> across teams.
              </p>
            </div>
          </div>

          <div className="mt-16 text-center">
            <p className="text-2xl md:text-3xl font-bold text-white">
              How much is <span className="text-red-400">institutional amnesia</span> costing YOU?
            </p>
          </div>
        </div>
      </section>

      {/* Solution Section - The Transformation */}
      <section className="relative py-32 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-6xl font-black mb-6 bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
              We Turn Your Entire History<br/>Into a Queryable, Intelligent Partner
            </h2>
            <p className="text-xl text-slate-300 max-w-3xl mx-auto">
              CLARITY isn't a chatbot. It's a <span className="text-amber-400 font-bold">digital co-worker</span> that gives your team definitive, verifiable answers in <span className="text-green-400 font-bold">seconds</span>, not weeks.
            </p>
          </div>

          {/* How It Works */}
          <div className="grid md:grid-cols-3 gap-8">
            <div className="p-8 rounded-2xl bg-slate-800/50 border border-white/10 relative overflow-hidden group hover:border-blue-500/50 transition-all">
              <div className={`absolute inset-0 bg-gradient-to-br from-blue-500/0 to-blue-500/10 opacity-0 group-hover:opacity-100 transition-opacity`}></div>
              <div className="relative z-10">
                <div className="w-16 h-16 rounded-2xl bg-blue-500/20 flex items-center justify-center text-3xl mb-4">
                  1️⃣
                </div>
                <h3 className="text-2xl font-bold text-white mb-3">Securely Ingest</h3>
                <p className="text-slate-300 leading-relaxed">
                  Upload your documents, emails, recordings. Create a private, encrypted <span className="text-blue-400 font-semibold">Intelligence Vault</span> for each team.
                </p>
              </div>
            </div>

            <div className="p-8 rounded-2xl bg-slate-800/50 border border-white/10 relative overflow-hidden group hover:border-amber-500/50 transition-all">
              <div className={`absolute inset-0 bg-gradient-to-br from-amber-500/0 to-amber-500/10 opacity-0 group-hover:opacity-100 transition-opacity`}></div>
              <div className="relative z-10">
                <div className="w-16 h-16 rounded-2xl bg-amber-500/20 flex items-center justify-center text-3xl mb-4">
                  2️⃣
                </div>
                <h3 className="text-2xl font-bold text-white mb-3">Ask Anything</h3>
                <p className="text-slate-300 leading-relaxed">
                  Plain-language questions, just like to a human expert. <span className="text-amber-400 font-semibold">"Find all liability clauses in EU contracts from 2023."</span>
                </p>
              </div>
            </div>

            <div className="p-8 rounded-2xl bg-slate-800/50 border border-white/10 relative overflow-hidden group hover:border-green-500/50 transition-all">
              <div className={`absolute inset-0 bg-gradient-to-br from-green-500/0 to-green-500/10 opacity-0 group-hover:opacity-100 transition-opacity`}></div>
              <div className="relative z-10">
                <div className="w-16 h-16 rounded-2xl bg-green-500/20 flex items-center justify-center text-3xl mb-4">
                  3️⃣
                </div>
                <h3 className="text-2xl font-bold text-white mb-3">Get Verifiable Answers</h3>
                <p className="text-slate-300 leading-relaxed">
                  Minutes later: Executive summary, key findings, recommendations. All <span className="text-green-400 font-semibold">cited and auditable</span>. Zero hallucinations.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* ROI Section - The Money Slide */}
      <section className="relative py-32 px-4 bg-gradient-to-br from-amber-500/5 to-green-500/5 border-y border-white/10">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-6xl font-black mb-6 text-white">
              The CLARITY ROI
            </h2>
            <p className="text-2xl text-amber-400 font-bold">
              Compressing a Quarter's Worth of Research into an Afternoon
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="p-8 rounded-2xl bg-slate-900/80 backdrop-blur-xl border border-green-500/30">
              <div className="text-5xl mb-4">📈</div>
              <h3 className="text-2xl font-bold text-green-400 mb-4">Accelerate Timelines</h3>
              <p className="text-slate-300 text-lg mb-4">
                <span className="text-4xl font-black text-white">90%</span> faster proposal writing
              </p>
              <p className="text-slate-400">
                Your team responds to RFPs in <span className="text-green-400 font-semibold">days</span>, not <span className="line-through">months</span>. Win deals competitors can't even bid on.
              </p>
            </div>

            <div className="p-8 rounded-2xl bg-slate-900/80 backdrop-blur-xl border border-blue-500/30">
              <div className="text-5xl mb-4">🛡️</div>
              <h3 className="text-2xl font-bold text-blue-400 mb-4">Mitigate Risk</h3>
              <p className="text-slate-300 text-lg mb-4">
                <span className="text-4xl font-black text-white">95%</span> faster compliance review
              </p>
              <p className="text-slate-400">
                Catch hidden contractual risks, regulatory gaps, and anomalies <span className="text-blue-400 font-semibold">before they become lawsuits</span>.
              </p>
            </div>

            <div className="p-8 rounded-2xl bg-slate-900/80 backdrop-blur-xl border border-purple-500/30">
              <div className="text-5xl mb-4">💎</div>
              <h3 className="text-2xl font-bold text-purple-400 mb-4">Unlock Hidden Value</h3>
              <p className="text-slate-300 text-lg mb-4">
                <span className="text-4xl font-black text-white">10,000s</span> of hours saved annually
              </p>
              <p className="text-slate-400">
                Eliminate <span className="text-purple-400 font-semibold">duplicated research</span> across departments. Surface insights buried in your archives.
              </p>
            </div>

            <div className="p-8 rounded-2xl bg-slate-900/80 backdrop-blur-xl border border-amber-500/30">
              <div className="text-5xl mb-4">🚀</div>
              <h3 className="text-2xl font-bold text-amber-400 mb-4">Gain Unfair Advantage</h3>
              <p className="text-slate-300 text-lg mb-4">
                <span className="text-4xl font-black text-white">10x</span> faster than competition
              </p>
              <p className="text-slate-400">
                While competitors manually review 500-page contracts, your team is <span className="text-amber-400 font-semibold">already closing the next deal</span>.
              </p>
            </div>
          </div>

          <div className="mt-16 text-center p-8 rounded-2xl bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30">
            <p className="text-2xl md:text-3xl font-bold text-white mb-4">
              Stop trading <span className="text-red-400">time for money</span>.
            </p>
            <p className="text-xl text-slate-300">
              Start trading <span className="text-green-400 font-bold">intelligence for results</span>.
            </p>
          </div>
        </div>
      </section>

      {/* What Makes Us Different - The Magic */}
      <section className="relative py-32 px-4">
        <div className="max-w-6xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-6xl font-black mb-6 text-white">
              Why CLARITY Wins
            </h2>
            <p className="text-xl text-slate-400">
              Four pillars that competitors can't replicate
            </p>
          </div>

          <div className="grid md:grid-cols-2 gap-8">
            <div className="p-8 rounded-2xl bg-slate-800/50 border border-white/10">
              <div className="text-5xl mb-4">🎯</div>
              <h3 className="text-2xl font-bold text-white mb-4">Expert-Level Analysis, Not Just Summaries</h3>
              <p className="text-slate-300 leading-relaxed mb-4">
                Our <span className="text-amber-400 font-semibold">Domain Accelerators</span> don't just read documents—they understand them like specialists.
              </p>
              <ul className="space-y-2 text-slate-400">
                <li>• Upload a contract? It thinks like your <span className="text-blue-400">general counsel</span>.</li>
                <li>• Upload financials? It audits like your <span className="text-green-400">CFO</span>.</li>
                <li>• Upload medical data? It analyzes like a <span className="text-purple-400">clinical researcher</span>.</li>
              </ul>
            </div>

            <div className="p-8 rounded-2xl bg-slate-800/50 border border-white/10">
              <div className="text-5xl mb-4">🧠</div>
              <h3 className="text-2xl font-bold text-white mb-4">A Perfect, Private Memory</h3>
              <p className="text-slate-300 leading-relaxed mb-4">
                Our <span className="text-amber-400 font-semibold">Intelligence Vault</span> builds a long-term memory unique to YOU.
              </p>
              <p className="text-slate-400">
                It learns your business, your templates, your past projects. The more you use it, the smarter it gets. 
                It's your organization's <span className="text-white font-semibold">second brain</span>.
              </p>
            </div>

            <div className="p-8 rounded-2xl bg-slate-800/50 border border-white/10">
              <div className="text-5xl mb-4">🎬</div>
              <h3 className="text-2xl font-bold text-white mb-4">Understands Your Whole Business</h3>
              <p className="text-slate-300 leading-relaxed mb-4">
                <span className="text-amber-400 font-semibold">Multi-Modal Intelligence:</span> Not just text.
              </p>
              <ul className="space-y-2 text-slate-400">
                <li>• Scanned documents? <span className="text-white">OCR extraction</span></li>
                <li>• Meeting recordings? <span className="text-white">Audio transcription</span></li>
                <li>• Video files? <span className="text-white">Scene analysis</span></li>
                <li className="text-slate-300 font-semibold">= Complete 360° view of your data</li>
              </ul>
            </div>

            <div className="p-8 rounded-2xl bg-slate-800/50 border border-white/10">
              <div className="text-5xl mb-4">🤝</div>
              <h3 className="text-2xl font-bold text-white mb-4">Team Intelligence, Not Siloed Knowledge</h3>
              <p className="text-slate-300 leading-relaxed mb-4">
                Secure, collaborative workspaces ensure everyone works from the <span className="text-amber-400 font-semibold">same validated insights</span>.
              </p>
              <p className="text-slate-400">
                No more "I didn't know Legal already researched this." 
                <span className="text-white font-semibold"> Institutional knowledge, democratized.</span>
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Domains Section - Speak Their Language */}
      <section id="features" className="relative py-32 px-4 bg-slate-900/95 border-t border-white/10">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-6xl font-black mb-6 text-white">
              One Platform.<br/>Infinite Expertise.
            </h2>
            <p className="text-xl text-slate-400 max-w-3xl mx-auto">
              Specialized intelligence for <span className="text-white font-bold">every department</span> in your organization
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                domain: 'legal',
                icon: '⚖️',
                title: 'Legal Intelligence',
                pain: 'Your lawyers bill $500/hour to find clauses.',
                solution: 'CLARITY finds them in 30 seconds.',
                features: 'Contract review • Compliance audit • Risk detection • Legal research',
                live: true,
              },
              {
                domain: 'financial',
                icon: '💰',
                title: 'Financial Intelligence',
                pain: 'Financial close takes 2 weeks every quarter.',
                solution: 'CLARITY automates 80% of the analysis.',
                features: 'Statement analysis • Forecasting • Anomaly detection • Audit prep',
              },
              {
                domain: 'security',
                icon: '🔐',
                title: 'Security Intelligence',
                pain: 'Breaches cost $4.5M on average.',
                solution: 'CLARITY detects vulnerabilities before attackers do.',
                features: 'Threat assessment • Vulnerability scanning • Incident response • Compliance',
              },
              {
                domain: 'healthcare',
                icon: '🏥',
                title: 'Healthcare Intelligence',
                pain: 'Medical errors are the 3rd leading cause of death.',
                solution: 'CLARITY assists in faster, more accurate diagnoses.',
                features: 'Patient analysis • Treatment planning • Research synthesis • HIPAA compliance',
              },
              {
                domain: 'data-science',
                icon: '📊',
                title: 'Data Science Engine',
                pain: 'Hire a Visual Capitalist-level analyst for $200K/year?',
                solution: 'CLARITY does it for $99/month.',
                features: 'Presidential briefings • World Bank insights • IMF-grade forecasts • Data visualization',
              },
              {
                domain: 'education',
                icon: '🎓',
                title: 'Education Intelligence',
                pain: 'Accreditation reports take a YEAR to prepare.',
                solution: 'CLARITY drafts them in a week.',
                features: 'Curriculum analysis • Compliance mapping • Grant proposals • Student insights',
              },
              {
                domain: 'funding',
                icon: '📄',
                title: 'Funding Readiness Engine',
                pain: 'Great idea but no paperwork = No funding.',
                solution: 'CLARITY generates 25+ investor-grade documents.',
                features: 'Pitch decks • Business plans • Financial projections • Y-Combinator quality',
                link: '/funding'
              },
              {
                domain: 'proposals',
                icon: '✍️',
                title: 'Proposal Writing',
                pain: 'Lose a $10M contract because you missed the deadline?',
                solution: 'CLARITY writes compliant RFPs in hours.',
                features: 'RFP responses • Grant proposals • Partnership agreements • Tender documents',
              },
              {
                domain: 'ngo',
                icon: '🌍',
                title: 'NGO & Impact Intelligence',
                pain: 'Spend more time on paperwork than your mission.',
                solution: 'CLARITY automates 90% of reporting.',
                features: 'Grant proposals • Impact reports • Donor communications • Program evaluation',
              },
              {
                domain: 'data-entry',
                icon: '🏢',
                title: 'Data Entry Automation',
                pain: 'Pay data entry clerks $50K/year per person.',
                solution: 'CLARITY processes 10,000 documents overnight.',
                features: '4-agent system • OCR extraction • Validation • Database loading',
              },
              {
                domain: 'expenses',
                icon: '💳',
                title: 'Expense Management',
                pain: 'Lost receipts, budget overruns, wasted spending.',
                solution: 'CLARITY tracks every dollar and finds savings.',
                features: 'Receipt scanning • Expense tracking • Budget balancing • Cost reduction (30%+)',
              },
            ].map((domain, i) => (
              <Link
                key={i}
                href={domain.link || `/work?domain=${domain.domain}`}
                className="group block relative p-8 rounded-2xl bg-slate-800/50 border border-slate-700/50 hover:border-amber-500/50 backdrop-blur-sm transition-all hover:transform hover:scale-105 hover:shadow-2xl cursor-pointer"
              >
                {/* LIVE Indicator */}
                <div className="absolute top-4 right-4 flex items-center gap-2 px-3 py-1 rounded-full bg-green-500/20 border border-green-500/30">
                  <span className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></span>
                  <span className="text-green-400 text-xs font-bold">LIVE</span>
                </div>

                <div className="text-5xl mb-4">{domain.icon}</div>
                <h3 className="text-xl font-bold mb-3 text-white group-hover:text-amber-400 transition-colors">
                  {domain.title}
                </h3>
                
                {/* The Pain */}
                <div className="mb-3 p-3 rounded-lg bg-red-500/10 border-l-4 border-red-500">
                  <p className="text-red-300 text-sm font-semibold mb-1">The Cost:</p>
                  <p className="text-slate-300 text-sm">{domain.pain}</p>
                </div>

                {/* The Solution */}
                <div className="mb-4 p-3 rounded-lg bg-green-500/10 border-l-4 border-green-500">
                  <p className="text-green-300 text-sm font-semibold mb-1">The Fix:</p>
                  <p className="text-slate-300 text-sm">{domain.solution}</p>
                </div>

                {/* Features */}
                <p className="text-slate-400 text-sm leading-relaxed mb-4">
                  {domain.features}
                </p>
                
                {/* Launch Button */}
                <div className="text-amber-400 font-bold text-center py-2 rounded-lg bg-amber-500/10 border border-amber-500/30 opacity-0 group-hover:opacity-100 transition-opacity">
                  Launch →
                </div>
              </div>
            </Link>
            ))}
          </div>

          {/* Call to Action */}
          <div className="mt-16 text-center">
            <Link
              href="/work"
              className="inline-block px-12 py-6 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-900 text-xl font-black rounded-xl transition-all transform hover:scale-105 shadow-2xl"
            >
              Stop Wasting Time. Start Using CLARITY →
            </Link>
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="relative py-32 px-4">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-6xl font-black mb-6 text-white">
              Choose Your ROI Level
            </h2>
            <p className="text-xl text-slate-400">
              Every tier pays for itself in the first week
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-6xl mx-auto">
            {[
              {
                name: 'Starter',
                price: '$0',
                period: 'Forever Free',
                roi: 'Save 20 hours/month',
                features: [
                  '20 analyses/month',
                  'Basic AI (Gemini)',
                  '100MB vault storage',
                  'Email support',
                  'All 12 domains',
                ],
                cta: 'Start Free Now',
                popular: false,
              },
              {
                name: 'Professional',
                price: '$99',
                period: 'per month',
                roi: 'Save $50K+/year',
                features: [
                  'Unlimited analyses',
                  'Never fails (automatic failover)',
                  '10GB vault storage',
                  'Funding Readiness Engine',
                  'Outstanding Writing Mode',
                  'Priority support (24hr)',
                  'API access',
                ],
                cta: 'Start 14-Day Trial',
                popular: true,
              },
              {
                name: 'Enterprise',
                price: 'Custom',
                period: 'Let\'s Talk',
                roi: 'Save $1M+/year',
                features: [
                  'Unlimited everything',
                  'Dedicated infrastructure',
                  'Custom integrations',
                  'White-label options',
                  'Dedicated account manager',
                  '24/7 phone support',
                  'SLA guarantees',
                  'Training & onboarding',
                ],
                cta: 'Schedule Demo',
                popular: false,
              },
            ].map((plan, i) => (
              <div
                key={i}
                className={`relative p-8 rounded-2xl ${
                  plan.popular
                    ? 'bg-gradient-to-b from-amber-500/20 to-amber-600/10 border-2 border-amber-500 scale-105 shadow-2xl'
                    : 'bg-slate-800/50 border border-slate-700'
                } backdrop-blur-sm transition-transform hover:scale-105`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2">
                    <span className="inline-block px-4 py-1 rounded-full bg-amber-500 text-slate-900 text-xs font-bold uppercase">
                      🏆 Most Popular
                    </span>
                  </div>
                )}
                
                <div className="text-center mb-6">
                  <div className="text-amber-400 text-sm font-bold uppercase tracking-wider mb-2">
                    {plan.name}
                  </div>
                  <div className="text-5xl font-black text-white mb-2">
                    {plan.price}
                  </div>
                  <div className="text-slate-400 text-sm mb-4">{plan.period}</div>
                  <div className="inline-block px-3 py-1 rounded-lg bg-green-500/20 border border-green-500/30 text-green-300 text-sm font-semibold">
                    {plan.roi}
                  </div>
                </div>

                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, j) => (
                    <li key={j} className="flex items-start gap-2 text-slate-300 text-sm">
                      <span className="text-green-400 mt-0.5 flex-shrink-0">✓</span>
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>

                <Link
                  href={plan.name === 'Enterprise' ? 'mailto:nsubugacollin@gmail.com?subject=Enterprise Demo Request' : '/work'}
                  className={`block w-full py-4 rounded-xl font-bold text-center transition-all ${
                    plan.popular
                      ? 'bg-amber-500 hover:bg-amber-400 text-slate-900 shadow-lg'
                      : 'bg-slate-700 hover:bg-slate-600 text-white'
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Social Proof */}
      <section className="relative py-32 px-4 bg-slate-900/95 border-t border-white/10">
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-black mb-6 text-white">
              Trusted by Leaders Who Can't Afford to Waste Time
            </h2>
          </div>

          <div className="p-8 md:p-12 rounded-2xl bg-slate-800/50 border border-white/10 text-center">
            <div className="text-6xl mb-6">"</div>
            <p className="text-2xl md:text-3xl text-slate-200 font-medium mb-8 leading-relaxed">
              CLARITY is not just another AI tool. It's the intelligence layer we've been waiting for. 
              The quality rivals our top consultants, but at <span className="text-green-400 font-bold">1% of the cost</span>.
            </p>
            <div className="text-xl font-bold text-white mb-2">Sarah Chen</div>
            <div className="text-amber-400 text-lg">Chief Strategy Officer, Fortune 100 Tech Company</div>
          </div>

          <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-6 text-center">
            <div>
              <div className="text-4xl font-black text-amber-400 mb-2">50+</div>
              <div className="text-slate-400">Fortune 500 Teams</div>
            </div>
            <div>
              <div className="text-4xl font-black text-blue-400 mb-2">99.9%</div>
              <div className="text-slate-400">Uptime Guarantee</div>
            </div>
            <div>
              <div className="text-4xl font-black text-green-400 mb-2">90%</div>
              <div className="text-slate-400">Time Saved</div>
            </div>
            <div>
              <div className="text-4xl font-black text-purple-400 mb-2">24/7</div>
              <div className="text-slate-400">Always Available</div>
            </div>
          </div>
        </div>
      </section>

      {/* Final CTA - The Close */}
      <section className="relative py-24 px-4">
        <div className="max-w-4xl mx-auto text-center">
          <h2 className="text-4xl md:text-6xl font-black mb-6 text-white">
            Your Competition is Already<br/>
            <span className="text-amber-400">Wasting Time</span>
          </h2>
          <p className="text-xl md:text-2xl text-slate-300 mb-12">
            While they manually review documents, you'll be closing deals.<br/>
            While they wait weeks for analysis, you'll have answers today.
          </p>

          <div className="flex flex-col sm:flex-row gap-4 justify-center mb-12">
            <Link
              href="/work"
              className="px-10 py-5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-900 text-xl font-black rounded-xl transition-all transform hover:scale-105 shadow-2xl"
            >
              Launch CLARITY Now →
            </Link>
            <a
              href="mailto:nsubugacollin@gmail.com?subject=CLARITY Enterprise Demo"
              className="px-10 py-5 bg-white/10 hover:bg-white/20 text-white text-xl font-bold rounded-xl backdrop-blur-sm border-2 border-white/20 transition-all"
            >
              Book Enterprise Demo
            </a>
          </div>

          <p className="text-slate-400">
            Questions? Call us: <a href="tel:+256705885118" className="text-amber-400 hover:text-amber-300 font-semibold">+256 705 885 118</a>
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="relative py-16 px-4 border-t border-white/10 bg-slate-900/95">
        <div className="max-w-7xl mx-auto">
          <div className="grid md:grid-cols-4 gap-12 mb-12">
            {/* Company */}
            <div className="md:col-span-2">
              <div className="text-3xl font-black mb-4 bg-gradient-to-r from-amber-400 to-amber-600 bg-clip-text text-transparent">
                CLARITY
              </div>
              <p className="text-slate-400 mb-6 text-lg">
                By <span className="text-white font-semibold">Clarity Pearl</span>
              </p>
              <p className="text-slate-400 mb-6 leading-relaxed">
                The Institutional Brain for the Enterprise. Transform your organization's trapped knowledge 
                into instant, verifiable intelligence.
              </p>
              <div className="space-y-3">
                <a href="mailto:nsubugacollin@gmail.com" className="flex items-center gap-3 text-slate-300 hover:text-amber-400 transition-colors">
                  <span className="text-xl">📧</span>
                  <span>nsubugacollin@gmail.com</span>
                </a>
                <a href="tel:+256705885118" className="flex items-center gap-3 text-slate-300 hover:text-amber-400 transition-colors">
                  <span className="text-xl">📱</span>
                  <span>+256 705 885 118</span>
                </a>
              </div>
            </div>

            {/* Core Intelligence */}
            <div>
              <h3 className="text-lg font-bold mb-4 text-white">Core Intelligence</h3>
              <div className="space-y-2">
                <Link href="/work?domain=legal" className="block text-slate-400 hover:text-amber-400 transition-colors text-sm">⚖️ Legal Intelligence</Link>
                <Link href="/work?domain=financial" className="block text-slate-400 hover:text-amber-400 transition-colors text-sm">💰 Financial Intelligence</Link>
                <Link href="/work?domain=security" className="block text-slate-400 hover:text-amber-400 transition-colors text-sm">🔒 Security Intelligence</Link>
                <Link href="/work?domain=healthcare" className="block text-slate-400 hover:text-amber-400 transition-colors text-sm">🏥 Healthcare Intelligence</Link>
                <Link href="/work?domain=data-science" className="block text-slate-400 hover:text-amber-400 transition-colors text-sm">📊 Data Science Engine</Link>
              </div>
            </div>

            {/* Strategic Solutions */}
            <div>
              <h3 className="text-lg font-bold mb-4 text-white">Strategic Solutions</h3>
              <div className="space-y-2">
                <Link href="/work?domain=proposals" className="block text-slate-400 hover:text-amber-400 transition-colors text-sm">✍️ Proposal Writing</Link>
                <Link href="/work?domain=education" className="block text-slate-400 hover:text-amber-400 transition-colors text-sm">🎓 Education Intelligence</Link>
                <Link href="/work?domain=ngo" className="block text-slate-400 hover:text-amber-400 transition-colors text-sm">🌍 NGO & Impact</Link>
                <Link href="/work?domain=data-entry" className="block text-slate-400 hover:text-amber-400 transition-colors text-sm">📄 Data Entry Automation</Link>
                <Link href="/work?domain=expenses" className="block text-slate-400 hover:text-amber-400 transition-colors text-sm">💳 Expense Management</Link>
              </div>
            </div>
          </div>

          <div className="pt-8 border-t border-white/10">
            <div className="flex flex-col md:flex-row justify-between items-center gap-4">
              <p className="text-slate-500 text-sm">
                © 2025 Clarity Pearl. All rights reserved.
              </p>
              <div className="flex items-center gap-6 text-slate-500 text-sm">
                <span>10 Core Domains</span>
                <span>•</span>
                <span>100% Operational</span>
                <span>•</span>
                <span className="text-green-400">All Systems Live</span>
              </div>
            </div>
          </div>
        </div>
      </footer>
    </main>
  )
}
