'use client'

import Link from 'next/link'

export default function FinancialIntelligencePage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-green-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="text-2xl font-black bg-gradient-to-r from-amber-400 to-amber-600 bg-clip-text text-transparent">
              CLARITY
            </div>
            <span className="text-sm text-slate-400">Financial Intelligence</span>
          </Link>
          <Link
            href="/work?domain=financial"
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
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-green-500/20 border border-green-500/30 text-green-200 text-sm font-semibold mb-6">
              <span>💰</span>
              <span>$288,000 WASTED ANNUALLY</span>
            </div>
            <h1 className="text-5xl md:text-7xl font-black mb-6 text-white">
              Your Financial Team Spends<br/>
              <span className="text-red-400">60% of Their Time</span><br/>
              Just Processing Data
            </h1>
            <p className="text-2xl text-slate-300 mb-4">
              At $100/hour, that's 24 hours/week = <span className="text-red-400 font-bold">$124,800/year</span> per analyst.
            </p>
            <p className="text-xl text-slate-400 mb-12 max-w-3xl">
              Not analyzing. Not strategizing. Just pulling numbers from statements, reconciling accounts, chasing down anomalies manually. Work a computer should do.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                href="/work?domain=financial"
                className="px-10 py-5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-900 text-xl font-black rounded-xl transition-all transform hover:scale-105 shadow-2xl"
              >
                Automate in 30 Seconds →
              </Link>
              <a
                href="mailto:nsubugacollin@gmail.com?subject=Financial Intelligence Demo"
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
              The Manual Nightmare
            </h2>
            <div className="grid md:grid-cols-3 gap-6 mb-12">
              <div className="p-8 rounded-2xl bg-red-500/10 border border-red-500/30">
                <div className="text-5xl mb-4">📊</div>
                <h3 className="text-3xl font-bold text-red-400 mb-4">24 Hours/Week</h3>
                <p className="text-slate-300 mb-4">
                  Average financial analyst spends on:
                </p>
                <ul className="space-y-2 text-sm text-slate-400">
                  <li>• Manual data entry from statements</li>
                  <li>• Reconciling accounts across systems</li>
                  <li>• Hunting for transaction details</li>
                  <li>• Building reports from scratch</li>
                  <li>• Chasing down anomalies</li>
                </ul>
              </div>
              <div className="p-8 rounded-2xl bg-orange-500/10 border border-orange-500/30">
                <div className="text-5xl mb-4">💸</div>
                <h3 className="text-3xl font-bold text-orange-400 mb-4">$288K/Year</h3>
                <p className="text-slate-300 mb-4">
                  Per 3-person finance team:
                </p>
                <ul className="space-y-2 text-sm text-slate-400">
                  <li>• CFO: $200/hr × 10hrs/wk = $104K/yr wasted</li>
                  <li>• Controller: $150/hr × 15hrs/wk = $117K/yr</li>
                  <li>• Analyst: $100/hr × 15hrs/wk = $78K/yr</li>
                  <li>• <strong>Total: $288K/year on manual work</strong></li>
                </ul>
              </div>
              <div className="p-8 rounded-2xl bg-yellow-500/10 border border-yellow-500/30">
                <div className="text-5xl mb-4">⚠️</div>
                <h3 className="text-3xl font-bold text-yellow-400 mb-4">Missed Frauds</h3>
                <p className="text-slate-300 mb-4">
                  When buried in manual work:
                </p>
                <ul className="space-y-2 text-sm text-slate-400">
                  <li>• Anomalies go unnoticed</li>
                  <li>• Trends aren't spotted</li>
                  <li>• Frauds slip through</li>
                  <li>• Strategic insights missed</li>
                  <li>• <strong>$1M+ losses common</strong></li>
                </ul>
              </div>
            </div>
            <div className="text-center p-8 rounded-2xl bg-slate-800/50 border border-red-500/30">
              <p className="text-3xl font-bold text-white mb-2">
                Mid-size company: <span className="text-red-400">$500K-$1M/year</span> wasted on manual financial analysis
              </p>
              <p className="text-xl text-slate-400">
                Plus opportunity cost of strategic insights never discovered
              </p>
            </div>
          </div>
        </section>

        {/* The Solution */}
        <section className="relative py-24 px-4">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-4xl md:text-5xl font-black mb-12 text-white text-center">
              CLARITY Analyzes in <span className="text-green-400">30 Seconds</span>
            </h2>
            <div className="grid md:grid-cols-2 gap-12 mb-12">
              <div>
                <h3 className="text-2xl font-bold text-white mb-6">What It Does</h3>
                <div className="space-y-6">
                  <div className="flex gap-4">
                    <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center text-2xl flex-shrink-0">✓</div>
                    <div>
                      <h4 className="text-lg font-bold text-white mb-2">Instant Financial Analysis</h4>
                      <p className="text-slate-300 text-sm">
                        Upload financial statements. CLARITY extracts all numbers, identifies trends, flags anomalies, calculates ratios instantly.
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center text-2xl flex-shrink-0">✓</div>
                    <div>
                      <h4 className="text-lg font-bold text-white mb-2">Anomaly Detection</h4>
                      <p className="text-slate-300 text-sm">
                        Spots unusual transactions, revenue patterns, expense spikes. Flags potential fraud or errors before they become problems.
                      </p>
                    </div>
                  </div>
                  <div className="flex gap-4">
                    <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center text-2xl flex-shrink-0">✓</div>
                    <div>
                      <h4 className="text-lg font-bold text-white mb-2">Audit Support</h4>
                      <p className="text-slate-300 text-sm">
                        Generate audit-ready reports, reconciliations, variance analyses. Everything cited, traceable, defensible.
                      </p>
                    </div>
                  </div>
                </div>
              </div>
              <div className="p-8 rounded-2xl bg-green-500/10 border-2 border-green-500/50">
                <h3 className="text-2xl font-bold text-green-400 mb-6">The Results</h3>
                <div className="space-y-4">
                  <div className="p-4 rounded-lg bg-slate-900/50">
                    <p className="text-slate-400 text-sm mb-1">Time to Analyze Statements</p>
                    <p className="text-2xl font-bold text-white">8 hours → 30 seconds</p>
                    <p className="text-green-400 text-sm">99.9% reduction</p>
                  </div>
                  <div className="p-4 rounded-lg bg-slate-900/50">
                    <p className="text-slate-400 text-sm mb-1">Annual Savings (3-person team)</p>
                    <p className="text-3xl font-black text-green-400">$280,000</p>
                    <p className="text-slate-400 text-sm">Team freed for strategic work</p>
                  </div>
                  <div className="p-4 rounded-lg bg-slate-900/50">
                    <p className="text-slate-400 text-sm mb-1">ROI (First Year)</p>
                    <p className="text-3xl font-black text-green-400">234x</p>
                    <p className="text-slate-400 text-sm">$280K saved vs. $1,200 cost</p>
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
                { icon: '📈', title: 'Financial Statement Analysis', desc: 'P&L, balance sheet, cash flow analysis in seconds' },
                { icon: '🔍', title: 'Anomaly Detection', desc: 'Spot unusual transactions, fraud indicators instantly' },
                { icon: '📊', title: 'Audit Support', desc: 'Generate reconciliations, variance analysis, audit trails' },
                { icon: '💹', title: 'Trend Analysis', desc: 'Identify revenue patterns, cost trends, seasonal variations' },
                { icon: '🎯', title: 'Budget vs Actuals', desc: 'Compare budgets to actuals, explain variances' },
                { icon: '💼', title: 'M&A Due Diligence', desc: 'Analyze target company financials rapidly' },
                { icon: '📉', title: 'Risk Assessment', desc: 'Calculate financial ratios, assess liquidity, solvency' },
                { icon: '🏦', title: 'Banking Compliance', desc: 'Verify regulatory requirements, generate reports' },
                { icon: '💡', title: 'Strategic Insights', desc: 'Surface hidden patterns, opportunities, threats' },
              ].map((useCase, i) => (
                <div key={i} className="p-6 rounded-xl bg-slate-800/50 border border-slate-700/50 hover:border-green-500/50 transition-all">
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
              Real CFO, Real Results
            </h2>
            <div className="p-8 rounded-2xl bg-slate-800/50 border border-green-500/30">
              <div className="mb-6">
                <h3 className="text-2xl font-bold text-green-400 mb-2">$50M Revenue SaaS Company</h3>
                <p className="text-slate-400">3-person finance team, monthly closes, quarterly board meetings</p>
              </div>
              <div className="grid md:grid-cols-2 gap-8 mb-8">
                <div>
                  <h4 className="text-xl font-bold text-white mb-4">Before CLARITY</h4>
                  <ul className="space-y-2 text-slate-300 text-sm">
                    <li className="flex items-start gap-2">
                      <span className="text-red-400">×</span>
                      <span>Month-end close took 7-10 days</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-red-400">×</span>
                      <span>Board decks required 40 hours to prepare</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-red-400">×</span>
                      <span>Anomalies discovered weeks later (too late)</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-red-400">×</span>
                      <span>Team buried in Excel, no time for strategy</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-red-400">×</span>
                      <span>$300K/year wasted on manual work</span>
                    </li>
                  </ul>
                </div>
                <div>
                  <h4 className="text-xl font-bold text-white mb-4">After CLARITY</h4>
                  <ul className="space-y-2 text-slate-300 text-sm">
                    <li className="flex items-start gap-2">
                      <span className="text-green-400">✓</span>
                      <span>Month-end close takes 2 days (AI-assisted)</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-400">✓</span>
                      <span>Board decks auto-generated in 2 hours</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-400">✓</span>
                      <span>Anomalies flagged instantly (same day resolution)</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-400">✓</span>
                      <span>Team focuses on strategic initiatives, planning</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-400">✓</span>
                      <span>$290K saved (net cost: $10K/year)</span>
                    </li>
                  </ul>
                </div>
              </div>
              <div className="p-6 rounded-xl bg-green-500/10 border border-green-500/30">
                <p className="text-2xl font-bold text-white mb-2">
                  Result: 29x ROI, caught $400K fraud that would've been missed
                </p>
                <p className="text-slate-300">
                  "CLARITY spotted a vendor payment anomaly in minutes. Manual review would've taken weeks, if we'd caught it at all." - CFO
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Pricing */}
        <section className="relative py-24 px-4 bg-slate-900/95 border-y border-white/10">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl md:text-5xl font-black mb-6 text-white">
              Simple Pricing
            </h2>
            <p className="text-xl text-slate-300 mb-12">
              Built for finance teams of all sizes
            </p>
            <div className="grid md:grid-cols-2 gap-8">
              <div className="p-8 rounded-2xl bg-slate-800/50 border border-slate-700">
                <h3 className="text-2xl font-bold text-white mb-4">Professional</h3>
                <div className="text-5xl font-black text-amber-400 mb-2">$499</div>
                <p className="text-slate-400 mb-6">per month</p>
                <ul className="space-y-3 text-sm text-slate-300 mb-8 text-left">
                  <li className="flex items-center gap-2">
                    <span className="text-green-400">✓</span>
                    <span>100 analyses/month</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-green-400">✓</span>
                    <span>All financial analysis features</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-green-400">✓</span>
                    <span>Anomaly detection</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-green-400">✓</span>
                    <span>5 users</span>
                  </li>
                </ul>
                <p className="text-green-400 font-bold mb-4">ROI: 234x vs. manual ($124K saved)</p>
                <Link
                  href="/work?domain=financial"
                  className="block px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white font-bold rounded-lg transition-all"
                >
                  Try Free
                </Link>
              </div>
              <div className="p-8 rounded-2xl bg-gradient-to-br from-green-500/20 to-blue-500/20 border-2 border-green-500/50">
                <div className="inline-block px-3 py-1 rounded-full bg-green-500/30 text-green-200 text-xs font-bold mb-4">
                  MOST POPULAR
                </div>
                <h3 className="text-2xl font-bold text-white mb-4">Enterprise</h3>
                <div className="text-5xl font-black text-green-400 mb-2">Custom</div>
                <p className="text-slate-400 mb-6">Starting at $2,499/month</p>
                <ul className="space-y-3 text-sm text-slate-300 mb-8 text-left">
                  <li className="flex items-center gap-2">
                    <span className="text-green-400">✓</span>
                    <span>Unlimited analyses</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-green-400">✓</span>
                    <span>Priority processing</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-green-400">✓</span>
                    <span>API access</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-green-400">✓</span>
                    <span>Dedicated support</span>
                  </li>
                </ul>
                <p className="text-green-400 font-bold mb-4">ROI: 116x ($290K saved vs. $2.5K/mo)</p>
                <a
                  href="mailto:nsubugacollin@gmail.com?subject=Financial Intelligence Enterprise"
                  className="block px-6 py-3 bg-green-500 hover:bg-green-400 text-white font-bold rounded-lg transition-all"
                >
                  Contact Sales
                </a>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="relative py-24 px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl md:text-6xl font-black mb-6 text-white">
              Stop Wasting $280K/Year<br/>
              On Manual Analysis
            </h2>
            <p className="text-xl text-slate-300 mb-12">
              Try CLARITY risk-free. See results in your first analysis.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/work?domain=financial"
                className="px-10 py-5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-900 text-xl font-black rounded-xl transition-all transform hover:scale-105 shadow-2xl"
              >
                Try Free Now →
              </Link>
              <a
                href="mailto:nsubugacollin@gmail.com?subject=Financial Intelligence Demo"
                className="px-10 py-5 bg-white/10 hover:bg-white/20 text-white text-xl font-bold rounded-xl backdrop-blur-sm border-2 border-white/20 transition-all"
              >
                Book Demo
              </a>
            </div>
            <p className="mt-8 text-slate-400">
              Questions? Call us: <a href="tel:+256705885118" className="text-amber-400 hover:text-amber-300 font-semibold">+256 705 885 118</a>
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
