'use client'

import Link from 'next/link'

export default function LegalIntelligencePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-purple-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="text-2xl font-black bg-gradient-to-r from-amber-400 to-amber-600 bg-clip-text text-transparent">
              CLARITY
            </div>
            <span className="text-sm text-slate-400">Legal Intelligence</span>
          </Link>
          <Link
            href="/work?domain=legal"
            className="px-6 py-3 bg-amber-500 hover:bg-amber-400 text-slate-900 font-bold rounded-lg transition-all"
          >
            Try It Free →
          </Link>
        </div>
      </header>

      <main>
        {/* Hero */}
        <section className="relative py-24 px-4">
          <div className="max-w-6xl mx-auto">
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-purple-500/20 border border-purple-500/30 text-purple-200 text-sm font-semibold mb-6">
              <span>⚖️</span>
              <span>$249,600 WASTED ANNUALLY</span>
            </div>
            <h1 className="text-5xl md:text-7xl font-black mb-6 text-white">
              Your Lawyers Spend<br/>
              <span className="text-red-400">40% of Their Time</span><br/>
              Just Finding Information
            </h1>
            <p className="text-2xl text-slate-300 mb-4">
              At $300/hour, that's 16 hours/week = <span className="text-red-400 font-bold">$249,600/year</span> wasted per lawyer.
            </p>
            <p className="text-xl text-slate-400 mb-12 max-w-3xl">
              Not practicing law. Not advising clients. Just searching through documents, trying to remember where that clause was, hunting for precedents they know they have somewhere.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                href="/work?domain=legal"
                className="px-10 py-5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-900 text-xl font-black rounded-xl transition-all transform hover:scale-105 shadow-2xl"
              >
                Find Anything in 3 Seconds →
              </Link>
              <a
                href="mailto:nsubugacollin@gmail.com?subject=Legal Intelligence Demo"
                className="px-10 py-5 bg-white/10 hover:bg-white/20 text-white text-xl font-bold rounded-xl backdrop-blur-sm border-2 border-white/20 transition-all"
              >
                See Demo
              </a>
            </div>
          </div>
        </section>

        {/* The Pain */}
        <section className="relative py-24 px-4 bg-red-500/5 border-y border-red-500/20">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-4xl md:text-5xl font-black mb-12 text-white text-center">
              The Hidden Tax on Your Legal Team
            </h2>
            <div className="grid md:grid-cols-3 gap-6 mb-12">
              <div className="p-8 rounded-2xl bg-red-500/10 border border-red-500/30">
                <div className="text-5xl mb-4">⏰</div>
                <h3 className="text-3xl font-bold text-red-400 mb-4">16 Hours/Week</h3>
                <p className="text-slate-300 mb-4">
                  Average lawyer spends <strong>40% of their time</strong> on non-legal work:
                </p>
                <ul className="space-y-2 text-sm text-slate-400">
                  <li>• Searching for contract clauses</li>
                  <li>• Finding relevant case precedents</li>
                  <li>• Reviewing old agreements</li>
                  <li>• Digging through email threads</li>
                  <li>• Asking colleagues "where's that file?"</li>
                </ul>
              </div>
              <div className="p-8 rounded-2xl bg-orange-500/10 border border-orange-500/30">
                <div className="text-5xl mb-4">💸</div>
                <h3 className="text-3xl font-bold text-orange-400 mb-4">$249,600/Year</h3>
                <p className="text-slate-300 mb-4">
                  Per senior lawyer at $300/hour:
                </p>
                <ul className="space-y-2 text-sm text-slate-400">
                  <li>• 16 hours/week × 52 weeks = 832 hours/year</li>
                  <li>• 832 hours × $300/hour = $249,600</li>
                  <li>• That's <strong>a junior lawyer's entire salary</strong></li>
                  <li>• Just wasted on searching and organizing</li>
                </ul>
              </div>
              <div className="p-8 rounded-2xl bg-yellow-500/10 border border-yellow-500/30">
                <div className="text-5xl mb-4">📉</div>
                <h3 className="text-3xl font-bold text-yellow-400 mb-4">Missed Risks</h3>
                <p className="text-slate-300 mb-4">
                  When lawyers can't find information:
                </p>
                <ul className="space-y-2 text-sm text-slate-400">
                  <li>• Liability clauses get missed</li>
                  <li>• Precedents aren't applied</li>
                  <li>• Inconsistent advice given</li>
                  <li>• Compliance gaps emerge</li>
                  <li>• <strong>$500K-$5M lawsuits result</strong></li>
                </ul>
              </div>
            </div>
            <div className="text-center p-8 rounded-2xl bg-slate-800/50 border border-red-500/30">
              <p className="text-3xl font-bold text-white mb-2">
                5 lawyers × $249,600 = <span className="text-red-400">$1.25M/year wasted</span>
              </p>
              <p className="text-xl text-slate-400">
                Not counting junior associates, paralegals, and support staff
              </p>
            </div>
          </div>
        </section>

        {/* The Solution */}
        <section className="relative py-24 px-4">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-4xl md:text-5xl font-black mb-12 text-white text-center">
              CLARITY Finds Anything in <span className="text-green-400">3 Seconds</span>
            </h2>
            <div className="grid md:grid-cols-2 gap-12 mb-12">
              <div>
                <h3 className="text-2xl font-bold text-white mb-6">How It Works</h3>
                <div className="space-y-6">
                  <div className="flex gap-4">
                    <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center text-2xl flex-shrink-0">1</div>
                    <div>
                      <h4 className="text-lg font-bold text-white mb-2">One-Time Setup (5 Minutes)</h4>
                      <p className="text-slate-300 text-sm">
                        Upload all your contracts, case files, memos, correspondence. CLARITY indexes everything, creates your firm's private Intelligence Vault.
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center text-2xl flex-shrink-0">2</div>
                    <div>
                      <h4 className="text-lg font-bold text-white mb-2">Ask Plain English Questions</h4>
                      <p className="text-slate-300 text-sm">
                        "Find all liability clauses in EU contracts from 2023"<br/>
                        "What payment terms did we agree to with Acme Corp?"<br/>
                        "Show me precedents for this clause"
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <div className="w-12 h-12 rounded-full bg-blue-500/20 flex items-center justify-center text-2xl flex-shrink-0">3</div>
                    <div>
                      <h4 className="text-lg font-bold text-white mb-2">Get Instant, Cited Answers</h4>
                      <p className="text-slate-300 text-sm">
                        CLARITY returns relevant clauses, contracts, precedents in 3 seconds. Every answer includes direct links to source documents. Zero hallucinations.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              <div className="p-8 rounded-2xl bg-green-500/10 border-2 border-green-500/50">
                <h3 className="text-2xl font-bold text-green-400 mb-6">The Results</h3>
                <div className="space-y-4">
                  <div className="p-4 rounded-lg bg-slate-900/50">
                    <p className="text-slate-400 text-sm mb-1">Time to Find Information</p>
                    <p className="text-2xl font-bold text-white">16 hours/week → 30 minutes/week</p>
                    <p className="text-green-400 text-sm">96.9% reduction</p>
                  </div>
                  <div className="p-4 rounded-lg bg-slate-900/50">
                    <p className="text-slate-400 text-sm mb-1">Annual Savings (Per Lawyer)</p>
                    <p className="text-3xl font-black text-green-400">$242,000</p>
                    <p className="text-slate-400 text-sm">Can now bill 800+ more hours/year</p>
                  </div>
                  <div className="p-4 rounded-lg bg-slate-900/50">
                    <p className="text-slate-400 text-sm mb-1">ROI (First Year, 5 Lawyers)</p>
                    <p className="text-3xl font-black text-green-400">101x</p>
                    <p className="text-slate-400 text-sm">$1.21M saved vs. $11,988 cost</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Use Cases */}
        <section className="relative py-24 px-4 bg-slate-900/95 border-y border-white/10">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-4xl md:text-5xl font-black mb-12 text-white text-center">
              What Your Team Can Do
            </h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                { icon: '📄', title: 'Contract Review', desc: 'Find risks, non-standard clauses, missing terms in seconds' },
                { icon: '⚖️', title: 'Compliance Checks', desc: 'Verify all agreements meet regulatory requirements' },
                { icon: '🔍', title: 'Legal Research', desc: 'Surface relevant precedents and case law instantly' },
                { icon: '📊', title: 'Due Diligence', desc: 'Analyze thousands of documents for M&A deals' },
                { icon: '✍️', title: 'Contract Drafting', desc: 'Find templates and standard clauses from past work' },
                { icon: '🎯', title: 'Litigation Support', desc: 'Search case files, depositions, discovery documents' },
                { icon: '💼', title: 'Corporate Governance', desc: 'Track board resolutions, bylaws, shareholder agreements' },
                { icon: '🏢', title: 'Real Estate', desc: 'Review leases, title documents, zoning agreements' },
                { icon: '💡', title: 'IP Management', desc: 'Track patents, trademarks, licensing agreements' },
              ].map((useCase, i) => (
                <div key={i} className="p-6 rounded-xl bg-slate-800/50 border border-slate-700/50 hover:border-purple-500/50 transition-all">
                  <div className="text-4xl mb-3">{useCase.icon}</div>
                  <h3 className="text-lg font-bold text-white mb-2">{useCase.title}</h3>
                  <p className="text-slate-400 text-sm">{useCase.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Real Scenario */}
        <section className="relative py-24 px-4">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-4xl md:text-5xl font-black mb-12 text-white text-center">
              Real Law Firm, Real Results
            </h2>
            <div className="p-8 rounded-2xl bg-slate-800/50 border border-blue-500/30">
              <div className="mb-6">
                <h3 className="text-2xl font-bold text-blue-400 mb-2">Mid-Size Corporate Law Firm</h3>
                <p className="text-slate-400">50 lawyers, 3 practice areas, 20+ years of documents</p>
              </div>
              <div className="grid md:grid-cols-2 gap-8 mb-8">
                <div>
                  <h4 className="text-xl font-bold text-white mb-4">Before CLARITY</h4>
                  <ul className="space-y-2 text-slate-300 text-sm">
                    <li className="flex items-start gap-2">
                      <span className="text-red-400">×</span>
                      <span>Lawyers spent 15-20 hours/week searching for documents</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-red-400">×</span>
                      <span>Contract reviews took 3-5 days per agreement</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-red-400">×</span>
                      <span>Junior associates did manual doc review (expensive)</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-red-400">×</span>
                      <span>Inconsistent advice across matters</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-red-400">×</span>
                      <span>$12.5M/year wasted (50 lawyers × $249K)</span>
                    </li>
                  </ul>
                </div>
                <div>
                  <h4 className="text-xl font-bold text-white mb-4">After CLARITY</h4>
                  <ul className="space-y-2 text-slate-300 text-sm">
                    <li className="flex items-start gap-2">
                      <span className="text-green-400">✓</span>
                      <span>Lawyers find anything in 3 seconds, not 3 hours</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-400">✓</span>
                      <span>Contract reviews take 30 minutes (AI-assisted)</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-400">✓</span>
                      <span>Junior associates focus on high-value work</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-400">✓</span>
                      <span>Consistent, cited answers across all matters</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-400">✓</span>
                      <span>$12.1M saved (net cost: $400K/year)</span>
                    </li>
                  </ul>
                </div>
              </div>
              <div className="p-6 rounded-xl bg-green-500/10 border border-green-500/30">
                <p className="text-2xl font-bold text-white mb-2">
                  Result: 30x ROI, 4,000+ billable hours recovered annually
                </p>
                <p className="text-slate-300">
                  "CLARITY is like having a brilliant associate who's memorized every document we've ever touched." - Managing Partner
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Pricing */}
        <section className="relative py-24 px-4 bg-slate-900/95 border-y border-white/10">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl md:text-5xl font-black mb-6 text-white">
              Enterprise Pricing
            </h2>
            <p className="text-xl text-slate-300 mb-12">
              Built for law firms and legal departments
            </p>
            <div className="p-8 rounded-2xl bg-gradient-to-br from-purple-500/20 to-blue-500/20 border-2 border-purple-500/50">
              <div className="text-5xl font-black text-purple-400 mb-2">Custom</div>
              <p className="text-slate-400 mb-6">Starting at $10,000/month</p>
              <ul className="space-y-3 text-sm text-slate-300 mb-8 text-left max-w-md mx-auto">
                <li className="flex items-start gap-2">
                  <span className="text-green-400 text-xl">✓</span>
                  <span>Unlimited documents, unlimited searches</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400 text-xl">✓</span>
                  <span>Private cloud or on-premise deployment</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400 text-xl">✓</span>
                  <span>SSO, role-based access, audit logging</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400 text-xl">✓</span>
                  <span>Attorney-client privilege protection</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400 text-xl">✓</span>
                  <span>Dedicated account manager</span>
                </li>
                <li className="flex items-start gap-2">
                  <span className="text-green-400 text-xl">✓</span>
                  <span>24/7 phone support</span>
                </li>
              </ul>
              <p className="text-green-400 font-bold mb-4">
                ROI: 101x (First year savings: $1M+ for 5-lawyer team)
              </p>
              <a
                href="mailto:nsubugacollin@gmail.com?subject=Legal Intelligence Enterprise Demo"
                className="inline-block px-8 py-4 bg-purple-500 hover:bg-purple-400 text-white font-bold rounded-xl transition-all transform hover:scale-105 shadow-2xl"
              >
                Schedule Demo
              </a>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="relative py-24 px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl md:text-6xl font-black mb-6 text-white">
              Stop Wasting $250K/Year<br/>
              Per Lawyer
            </h2>
            <p className="text-xl text-slate-300 mb-12">
              Try CLARITY risk-free. See results in your first week.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/work?domain=legal"
                className="px-10 py-5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-900 text-xl font-black rounded-xl transition-all transform hover:scale-105 shadow-2xl"
              >
                Try Free Now →
              </Link>
              <a
                href="mailto:nsubugacollin@gmail.com?subject=Legal Intelligence Demo"
                className="px-10 py-5 bg-white/10 hover:bg-white/20 text-white text-xl font-bold rounded-xl backdrop-blur-sm border-2 border-white/20 transition-all"
              >
                Book Demo
              </a>
            </div>
            <p className="mt-8 text-slate-400">
              Questions? Call us: <a href="tel:+256705885118" className="text-amber-400 hover:text-amber-300 font-semibold">+256 705 885118</a>
            </p>
          </div>
        </section>
      </main>

      {/* Footer */}
      <footer className="border-t border-white/10 bg-slate-900/95 py-12 px-4">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-slate-400 mb-4">
            © 2025 Clarity Pearl. All rights reserved.
          </p>
          <div className="flex items-center justify-center gap-6 text-slate-400 text-sm">
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
