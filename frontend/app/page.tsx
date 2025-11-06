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
            <span>🏆</span>
            <span>Fortune 500 Grade Intelligence</span>
          </div>

          {/* Main Heading */}
          <h1 className="text-6xl md:text-8xl font-black mb-6 bg-gradient-to-r from-white via-blue-100 to-white bg-clip-text text-transparent animate-fade-in-up">
            CLARITY
          </h1>

          {/* Subtitle */}
          <p className="text-xl md:text-2xl text-slate-300 mb-12 max-w-4xl mx-auto animate-fade-in-up delay-200">
            The World's Most Advanced AI Intelligence Platform.<br />
            Presidential-Grade Analysis. Y-Combinator Quality. Fortune 50 Results.
          </p>

          {/* CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in-up delay-400">
            <Link 
              href="/register" 
              className="px-8 py-4 bg-amber-500 hover:bg-amber-400 text-slate-900 font-bold rounded-xl transition-all transform hover:scale-105 hover:shadow-2xl"
            >
              Start Free Trial →
            </Link>
            <Link 
              href="#features" 
              className="px-8 py-4 bg-white/10 hover:bg-white/20 text-white font-semibold rounded-xl backdrop-blur-sm border border-white/20 transition-all"
            >
              Explore Features
            </Link>
          </div>

          {/* API Status */}
          {apiStatus && (
            <div className="mt-12 inline-block px-4 py-2 rounded-lg bg-green-500/20 border border-green-500/30 text-green-200 text-sm">
              <span className="inline-block w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></span>
              API Status: {apiStatus.status} • Version {apiStatus.version}
            </div>
          )}
        </div>
      </section>

      {/* Stats Section */}
      <section className="relative py-20 bg-slate-900/80 backdrop-blur-xl border-t border-white/10">
        <div className="max-w-7xl mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { number: '50+', label: 'Fortune 500 Companies' },
              { number: '99.9%', label: 'Uptime Guarantee' },
              { number: '4', label: 'AI Models (Never Fails)' },
              { number: '11', label: 'Domain Accelerators' },
            ].map((stat, i) => (
              <div key={i} className="text-center">
                <div className="text-4xl md:text-5xl font-black bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent mb-2">
                  {stat.number}
                </div>
                <div className="text-slate-400 text-sm">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative py-32 px-4">
        <div className="max-w-7xl mx-auto">
          {/* Section Header */}
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-6xl font-black mb-6 bg-gradient-to-r from-white to-slate-300 bg-clip-text text-transparent">
              Presidential-Level Intelligence
            </h2>
            <p className="text-xl text-slate-400 max-w-3xl mx-auto">
              Every feature designed to outperform Fortune 50, Y-Combinator, and Crunchbase standards
            </p>
          </div>

          {/* Features Grid */}
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: '🚀',
                title: 'Multi-LLM Failover',
                description: '4 AI models (Gemini, GPT-4, Claude, Groq) with intelligent routing. If one fails, we switch instantly.',
              },
              {
                icon: '📄',
                title: 'Funding Readiness Engine',
                description: 'Generate 25+ documents at Fortune 50 / Y-Combinator / Presidential quality.',
              },
              {
                icon: '✨',
                title: 'Outstanding Writing System',
                description: '5-pass refinement: Substance → Emotion → Polish → Relevance → Perfection.',
              },
              {
                icon: '🏛️',
                title: '11 Domain Accelerators',
                description: 'Legal, Financial, Security, Healthcare, and more. All at presidential grade.',
              },
              {
                icon: '🤝',
                title: 'Interactive Planning',
                description: 'We ask questions, understand your vision, and plan with you before generating.',
              },
              {
                icon: '🔐',
                title: 'Enterprise Security',
                description: 'SOC2, GDPR, HIPAA compliant. End-to-end encryption. Fortress-level secure.',
              },
            ].map((feature, i) => (
              <div
                key={i}
                className="group p-8 rounded-2xl bg-slate-800/50 border border-slate-700/50 hover:border-blue-500/50 backdrop-blur-sm transition-all hover:transform hover:scale-105 hover:shadow-2xl cursor-pointer"
              >
                <div className="text-5xl mb-4">{feature.icon}</div>
                <h3 className="text-xl font-bold mb-3 text-white group-hover:text-blue-400 transition-colors">
                  {feature.title}
                </h3>
                <p className="text-slate-400 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section className="relative py-32 px-4 bg-slate-900/80">
        <div className="max-w-7xl mx-auto">
          <div className="text-center mb-20">
            <h2 className="text-4xl md:text-6xl font-black mb-6 text-white">
              Choose Your Power Level
            </h2>
            <p className="text-xl text-slate-400">
              From startups to presidents, we scale with you
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              {
                name: 'Starter',
                price: '$0',
                period: 'Forever Free',
                features: ['10 analyses/month', 'Basic AI models', '100MB storage', 'Email support'],
                cta: 'Start Free',
                featured: false,
              },
              {
                name: 'Professional',
                price: '$99',
                period: 'per month',
                features: ['1,000 analyses/month', 'All AI models + failover', '10GB storage', 'Funding Engine', 'Outstanding Writing', 'Priority support'],
                cta: 'Start Trial',
                featured: true,
              },
              {
                name: 'Enterprise',
                price: 'Custom',
                period: 'Contact Sales',
                features: ['Unlimited everything', 'Dedicated infrastructure', 'Custom integrations', 'White-label options', '24/7 support', 'SLA guarantees'],
                cta: 'Contact Us',
                featured: false,
              },
            ].map((plan, i) => (
              <div
                key={i}
                className={`p-8 rounded-2xl ${
                  plan.featured
                    ? 'bg-gradient-to-b from-blue-600/20 to-purple-600/20 border-2 border-blue-500 scale-105'
                    : 'bg-slate-800/50 border border-slate-700'
                } backdrop-blur-sm`}
              >
                {plan.featured && (
                  <div className="text-center mb-4">
                    <span className="inline-block px-3 py-1 rounded-full bg-amber-500 text-slate-900 text-xs font-bold">
                      🏆 MOST POPULAR
                    </span>
                  </div>
                )}
                <div className="text-center mb-6">
                  <div className="text-amber-400 text-sm font-semibold uppercase tracking-wider mb-2">
                    {plan.name}
                  </div>
                  <div className="text-5xl font-black text-white mb-2">
                    {plan.price}
                  </div>
                  <div className="text-slate-400 text-sm">{plan.period}</div>
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, j) => (
                    <li key={j} className="flex items-start gap-2 text-slate-300 text-sm">
                      <span className="text-green-400 mt-0.5">✓</span>
                      <span>{feature}</span>
                    </li>
                  ))}
                </ul>
                <Link
                  href="/register"
                  className={`block w-full py-3 rounded-xl font-semibold text-center transition-all ${
                    plan.featured
                      ? 'bg-amber-500 hover:bg-amber-400 text-slate-900'
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

      {/* Footer */}
      <footer className="relative py-12 px-4 border-t border-white/10">
        <div className="max-w-7xl mx-auto text-center">
          <p className="text-slate-400 mb-4">
            © 2025 CLARITY Engine. Fortune 500 Grade Intelligence Platform.
          </p>
          <div className="flex flex-wrap justify-center gap-6 text-sm text-slate-500">
            <Link href="/docs" className="hover:text-amber-400 transition-colors">Documentation</Link>
            <Link href="/api" className="hover:text-amber-400 transition-colors">API</Link>
            <Link href="/about" className="hover:text-amber-400 transition-colors">About</Link>
            <Link href="/support" className="hover:text-amber-400 transition-colors">Support</Link>
            <Link href="/privacy" className="hover:text-amber-400 transition-colors">Privacy</Link>
          </div>
        </div>
      </footer>
    </main>
  )
}
