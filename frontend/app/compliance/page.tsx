'use client'

import Link from 'next/link'

export default function ComplianceAuditsPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
      {/* Header */}
      <header className="border-b border-white/10 bg-slate-900/50 backdrop-blur-xl sticky top-0 z-50">
        <div className="max-w-7xl mx-auto px-4 py-4 flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="text-2xl font-black bg-gradient-to-r from-amber-400 to-amber-600 bg-clip-text text-transparent">
              CLARITY
            </div>
            <span className="text-sm text-slate-400">Compliance Audits</span>
          </Link>
          <Link
            href="/work?domain=security"
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
            <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-red-500/20 border border-red-500/30 text-red-200 text-sm font-semibold mb-6">
              <span>💰</span>
              <span>$800,000 SAVED ANNUALLY</span>
            </div>
            <h1 className="text-5xl md:text-7xl font-black mb-6 text-white">
              Security Questionnaires Take<br/>
              <span className="text-red-400">400 Hours</span>
            </h1>
            <p className="text-2xl md:text-3xl text-slate-300 mb-4">
              You have 20 of them.
            </p>
            <p className="text-xl text-slate-400 mb-12 max-w-3xl">
              That's 8,000 hours. That's <span className="text-red-400 font-bold">$800,000/year</span> at $100/hour. That's deals delayed by 3-6 months. That's revenue lost.
            </p>
            <div className="flex flex-col sm:flex-row gap-4">
              <Link
                href="/work?domain=security"
                className="px-10 py-5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-900 text-xl font-black rounded-xl transition-all transform hover:scale-105 shadow-2xl"
              >
                Answer in 5 Minutes →
              </Link>
              <a
                href="mailto:nsubugacollin@gmail.com?subject=Compliance Audits Demo"
                className="px-10 py-5 bg-white/10 hover:bg-white/20 text-white text-xl font-bold rounded-xl backdrop-blur-sm border-2 border-white/20 transition-all"
              >
                See Demo
              </a>
            </div>
          </div>
        </section>

        {/* The Cost */}
        <section className="relative py-24 px-4 bg-red-500/5 border-y border-red-500/20">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-4xl md:text-5xl font-black mb-12 text-white text-center">
              What It's <span className="text-red-400">Really</span> Costing You
            </h2>
            <div className="grid md:grid-cols-2 gap-8">
              <div className="p-8 rounded-2xl bg-red-500/10 border border-red-500/30">
                <div className="text-5xl mb-4">⏰</div>
                <h3 className="text-3xl font-bold text-red-400 mb-4">400 Hours Per Questionnaire</h3>
                <ul className="space-y-3 text-slate-300">
                  <li className="flex items-start gap-3">
                    <span className="text-red-400 mt-1">•</span>
                    <span><strong>Security officer:</strong> 200 hours gathering information</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-red-400 mt-1">•</span>
                    <span><strong>Legal team:</strong> 100 hours reviewing answers</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-red-400 mt-1">•</span>
                    <span><strong>Engineering:</strong> 50 hours providing technical details</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-red-400 mt-1">•</span>
                    <span><strong>Compliance:</strong> 50 hours coordinating and editing</span>
                  </li>
                </ul>
                <div className="mt-6 p-4 rounded-lg bg-red-900/30">
                  <p className="text-2xl font-bold text-white">$40,000 per questionnaire</p>
                  <p className="text-slate-400 text-sm">at $100/hour average</p>
                </div>
              </div>

              <div className="p-8 rounded-2xl bg-orange-500/10 border border-orange-500/30">
                <div className="text-5xl mb-4">💸</div>
                <h3 className="text-3xl font-bold text-orange-400 mb-4">The Hidden Costs</h3>
                <ul className="space-y-3 text-slate-300">
                  <li className="flex items-start gap-3">
                    <span className="text-orange-400 mt-1">•</span>
                    <span><strong>Deal delays:</strong> 3-6 months while you complete paperwork</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-orange-400 mt-1">•</span>
                    <span><strong>Lost deals:</strong> Prospects go with competitors who respond faster</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-orange-400 mt-1">•</span>
                    <span><strong>Team burnout:</strong> Your best people waste time on repetitive work</span>
                  </li>
                  <li className="flex items-start gap-3">
                    <span className="text-orange-400 mt-1">•</span>
                    <span><strong>Inconsistency:</strong> Different answers to the same questions</span>
                  </li>
                </ul>
                <div className="mt-6 p-4 rounded-lg bg-orange-900/30">
                  <p className="text-2xl font-bold text-white">Opportunity cost: Millions</p>
                  <p className="text-slate-400 text-sm">in delayed or lost revenue</p>
                </div>
              </div>
            </div>

            <div className="mt-12 text-center">
              <p className="text-3xl md:text-4xl font-bold text-white mb-4">
                20 questionnaires × $40,000 = <span className="text-red-400">$800,000/year</span>
              </p>
              <p className="text-xl text-slate-400">
                That's a junior engineer's salary. Every. Single. Year. Just for paperwork.
              </p>
            </div>
          </div>
        </section>

        {/* The Fix */}
        <section className="relative py-24 px-4">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-4xl md:text-5xl font-black mb-12 text-white text-center">
              CLARITY Answers in <span className="text-green-400">5 Minutes</span>
            </h2>
            
            <div className="grid md:grid-cols-3 gap-6 mb-12">
              <div className="p-6 rounded-2xl bg-slate-800/50 border border-green-500/30">
                <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center text-2xl mb-4">1</div>
                <h3 className="text-xl font-bold text-white mb-3">Upload Questionnaire</h3>
                <p className="text-slate-300">
                  SOC 2, HIPAA, ISO 27001, vendor security assessment - any format, any length
                </p>
              </div>
              <div className="p-6 rounded-2xl bg-slate-800/50 border border-green-500/30">
                <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center text-2xl mb-4">2</div>
                <h3 className="text-xl font-bold text-white mb-3">CLARITY Analyzes</h3>
                <p className="text-slate-300">
                  Scans your existing policies, security docs, certifications - finds all the answers
                </p>
              </div>
              <div className="p-6 rounded-2xl bg-slate-800/50 border border-green-500/30">
                <div className="w-12 h-12 rounded-full bg-green-500/20 flex items-center justify-center text-2xl mb-4">3</div>
                <h3 className="text-xl font-bold text-white mb-3">Review & Submit</h3>
                <p className="text-slate-300">
                  Get complete, accurate, cited answers in 5 minutes. Review, approve, send
                </p>
              </div>
            </div>

            <div className="p-8 rounded-2xl bg-green-500/10 border-2 border-green-500/50">
              <div className="grid md:grid-cols-2 gap-8">
                <div>
                  <h3 className="text-2xl font-bold text-green-400 mb-4">What You Get</h3>
                  <ul className="space-y-3 text-slate-300">
                    <li className="flex items-start gap-3">
                      <span className="text-green-400 text-xl">✓</span>
                      <span><strong>Complete answers</strong> to all questions (even the tricky ones)</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <span className="text-green-400 text-xl">✓</span>
                      <span><strong>Direct citations</strong> to your source documents</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <span className="text-green-400 text-xl">✓</span>
                      <span><strong>Consistent answers</strong> across all questionnaires</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <span className="text-green-400 text-xl">✓</span>
                      <span><strong>Editable format</strong> for final review</span>
                    </li>
                    <li className="flex items-start gap-3">
                      <span className="text-green-400 text-xl">✓</span>
                      <span><strong>Audit trail</strong> of how each answer was derived</span>
                    </li>
                  </ul>
                </div>
                <div>
                  <h3 className="text-2xl font-bold text-green-400 mb-4">The ROI</h3>
                  <div className="space-y-4">
                    <div className="p-4 rounded-lg bg-slate-900/50">
                      <p className="text-slate-400 text-sm mb-1">Time Saved</p>
                      <p className="text-2xl font-bold text-white">400 hours → 5 minutes</p>
                      <p className="text-green-400 text-sm">99.98% reduction</p>
                    </div>
                    <div className="p-4 rounded-lg bg-slate-900/50">
                      <p className="text-slate-400 text-sm mb-1">Cost Per Questionnaire</p>
                      <p className="text-2xl font-bold text-white">$40,000 → $500</p>
                      <p className="text-green-400 text-sm">98.75% savings</p>
                    </div>
                    <div className="p-4 rounded-lg bg-slate-900/50">
                      <p className="text-slate-400 text-sm mb-1">Annual Savings (20 questionnaires)</p>
                      <p className="text-3xl font-black text-green-400">$790,000</p>
                      <p className="text-slate-400 text-sm">First year ROI: 6,592%</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Proof */}
        <section className="relative py-24 px-4 bg-slate-900/95 border-y border-white/10">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-4xl md:text-5xl font-black mb-12 text-white text-center">
              Real Scenario
            </h2>
            <div className="p-8 rounded-2xl bg-slate-800/50 border border-blue-500/30">
              <div className="mb-6">
                <h3 className="text-2xl font-bold text-blue-400 mb-2">Fortune 500 Tech Company</h3>
                <p className="text-slate-400">Selling to healthcare and financial services enterprises</p>
              </div>
              <div className="grid md:grid-cols-2 gap-8 mb-8">
                <div>
                  <h4 className="text-xl font-bold text-white mb-4">Before CLARITY</h4>
                  <ul className="space-y-2 text-slate-300 text-sm">
                    <li className="flex items-start gap-2">
                      <span className="text-red-400">×</span>
                      <span>Received 50+ security questionnaires/year</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-red-400">×</span>
                      <span>Security team spent 3-4 weeks per questionnaire</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-red-400">×</span>
                      <span>Pulled in legal, engineering, compliance for each one</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-red-400">×</span>
                      <span>Deals delayed 2-6 months waiting for responses</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-red-400">×</span>
                      <span>Lost 3 major deals ($15M ARR) to faster competitors</span>
                    </li>
                  </ul>
                </div>
                <div>
                  <h4 className="text-xl font-bold text-white mb-4">After CLARITY</h4>
                  <ul className="space-y-2 text-slate-300 text-sm">
                    <li className="flex items-start gap-2">
                      <span className="text-green-400">✓</span>
                      <span>Same 50+ questionnaires/year</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-400">✓</span>
                      <span>Security team spends 30 minutes reviewing CLARITY's draft</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-400">✓</span>
                      <span>Legal/engineering only pulled in for edge cases (5%)</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-400">✓</span>
                      <span>Respond same day or next day</span>
                    </li>
                    <li className="flex items-start gap-2">
                      <span className="text-green-400">✓</span>
                      <span>Close deals 3x faster, win more competitive situations</span>
                    </li>
                  </ul>
                </div>
              </div>
              <div className="p-6 rounded-xl bg-green-500/10 border border-green-500/30">
                <p className="text-2xl font-bold text-white mb-2">Result: $2M saved annually</p>
                <p className="text-slate-300">
                  Security team freed up to focus on actual security improvements instead of paperwork. Sales cycle shortened by 60%. Win rate improved by 25%.
                </p>
              </div>
            </div>
          </div>
        </section>

        {/* Features */}
        <section className="relative py-24 px-4">
          <div className="max-w-6xl mx-auto">
            <h2 className="text-4xl md:text-5xl font-black mb-12 text-white text-center">
              Enterprise-Grade Features
            </h2>
            <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
              {[
                { icon: '📋', title: 'SOC 2 Questionnaires', desc: 'Type I & II, any format' },
                { icon: '🏥', title: 'HIPAA Compliance', desc: 'BAA requirements, PHI handling' },
                { icon: '🔒', title: 'Vendor Security', desc: 'VSAQ, CAIQ, custom assessments' },
                { icon: '📊', title: 'ISO 27001', desc: 'Full framework documentation' },
                { icon: '🛡️', title: 'NIST CSF', desc: 'Cybersecurity framework mapping' },
                { icon: '🌍', title: 'GDPR/Privacy', desc: 'Data protection questionnaires' },
                { icon: '💳', title: 'PCI DSS', desc: 'Payment card compliance' },
                { icon: '🏦', title: 'Financial Services', desc: 'GLBA, SOX requirements' },
                { icon: '⚙️', title: 'Custom Frameworks', desc: 'Your proprietary standards' },
              ].map((feature, i) => (
                <div key={i} className="p-6 rounded-xl bg-slate-800/50 border border-slate-700/50 hover:border-blue-500/50 transition-all">
                  <div className="text-4xl mb-3">{feature.icon}</div>
                  <h3 className="text-lg font-bold text-white mb-2">{feature.title}</h3>
                  <p className="text-slate-400 text-sm">{feature.desc}</p>
                </div>
              ))}
            </div>
          </div>
        </section>

        {/* Pricing */}
        <section className="relative py-24 px-4 bg-slate-900/95 border-y border-white/10">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl md:text-5xl font-black mb-6 text-white">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-slate-300 mb-12">
              Pay per questionnaire or subscribe for unlimited access
            </p>
            <div className="grid md:grid-cols-2 gap-8">
              <div className="p-8 rounded-2xl bg-slate-800/50 border border-slate-700">
                <h3 className="text-2xl font-bold text-white mb-4">Pay-Per-Use</h3>
                <div className="text-5xl font-black text-amber-400 mb-2">$500</div>
                <p className="text-slate-400 mb-6">per questionnaire</p>
                <ul className="space-y-3 text-sm text-slate-300 mb-8">
                  <li className="flex items-center gap-2">
                    <span className="text-green-400">✓</span>
                    <span>Complete analysis in 5 minutes</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-green-400">✓</span>
                    <span>Unlimited questions per questionnaire</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-green-400">✓</span>
                    <span>All frameworks supported</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-green-400">✓</span>
                    <span>No commitment</span>
                  </li>
                </ul>
                <p className="text-green-400 font-bold mb-4">ROI: 8,000% vs. manual ($40,000)</p>
                <Link
                  href="/work?domain=security"
                  className="block px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white font-bold rounded-lg transition-all"
                >
                  Try Free
                </Link>
              </div>
              <div className="p-8 rounded-2xl bg-gradient-to-br from-blue-500/20 to-purple-500/20 border-2 border-blue-500/50">
                <div className="inline-block px-3 py-1 rounded-full bg-blue-500/30 text-blue-200 text-xs font-bold mb-4">
                  MOST POPULAR
                </div>
                <h3 className="text-2xl font-bold text-white mb-4">Unlimited</h3>
                <div className="text-5xl font-black text-blue-400 mb-2">$2,499</div>
                <p className="text-slate-400 mb-6">per month</p>
                <ul className="space-y-3 text-sm text-slate-300 mb-8">
                  <li className="flex items-center gap-2">
                    <span className="text-green-400">✓</span>
                    <span>Everything in Pay-Per-Use</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-green-400">✓</span>
                    <span>Unlimited questionnaires</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-green-400">✓</span>
                    <span>Priority processing</span>
                  </li>
                  <li className="flex items-center gap-2">
                    <span className="text-green-400">✓</span>
                    <span>Team collaboration features</span>
                  </li>
                </ul>
                <p className="text-green-400 font-bold mb-4">Break-even at 5 questionnaires/month</p>
                <Link
                  href="mailto:nsubugacollin@gmail.com?subject=Compliance Audits Unlimited Plan"
                  className="block px-6 py-3 bg-blue-500 hover:bg-blue-400 text-white font-bold rounded-lg transition-all"
                >
                  Contact Sales
                </Link>
              </div>
            </div>
          </div>
        </section>

        {/* CTA */}
        <section className="relative py-24 px-4">
          <div className="max-w-4xl mx-auto text-center">
            <h2 className="text-4xl md:text-6xl font-black mb-6 text-white">
              Stop Losing Money on Paperwork
            </h2>
            <p className="text-xl text-slate-300 mb-12">
              Try CLARITY risk-free. Answer your next security questionnaire in 5 minutes instead of 400 hours.
            </p>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <Link
                href="/work?domain=security"
                className="px-10 py-5 bg-gradient-to-r from-amber-500 to-amber-600 hover:from-amber-400 hover:to-amber-500 text-slate-900 text-xl font-black rounded-xl transition-all transform hover:scale-105 shadow-2xl"
              >
                Try Free Now →
              </Link>
              <a
                href="mailto:nsubugacollin@gmail.com?subject=Compliance Audits Demo"
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
