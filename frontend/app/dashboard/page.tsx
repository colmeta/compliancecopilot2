'use client'

import { useState } from 'react'
import Link from 'next/link'

interface Domain {
  id: string
  name: string
  icon: string
  color: string
  description: string
  link?: string
}

export default function Dashboard() {
  const domains: Domain[] = [
    { id: 'legal', name: 'Legal Intelligence', icon: '⚖️', color: 'from-blue-500 to-cyan-500', description: 'Contract analysis, compliance, legal research', link: '/analyze/legal' },
    { id: 'financial', name: 'Financial Intelligence', icon: '💰', color: 'from-green-500 to-emerald-500', description: 'Financial modeling, forecasting, analysis', link: '/analyze/financial' },
    { id: 'security', name: 'Security Intelligence', icon: '🔐', color: 'from-red-500 to-pink-500', description: 'Threat detection, vulnerability assessment', link: '/analyze/security' },
    { id: 'healthcare', name: 'Healthcare Intelligence', icon: '🏥', color: 'from-purple-500 to-violet-500', description: 'Medical research, patient analysis, HIPAA compliance', link: '/analyze/healthcare' },
    { id: 'data-science', name: 'Data Science Engine', icon: '📊', color: 'from-amber-500 to-orange-500', description: 'World Bank / IMF grade insights', link: '/analyze/data-science' },
    { id: 'education', name: 'Education Intelligence', icon: '🎓', color: 'from-indigo-500 to-blue-500', description: 'Curriculum analysis, accreditation reports', link: '/analyze/education' },
    { id: 'proposals', name: 'Proposal Writing', icon: '✍️', color: 'from-teal-500 to-cyan-500', description: 'RFPs, grants, tenders - Win every bid', link: '/analyze/proposals' },
    { id: 'ngo', name: 'NGO & Impact', icon: '🌍', color: 'from-lime-500 to-green-500', description: 'Grant proposals, impact reports', link: '/analyze/ngo' },
    { id: 'funding', name: 'Funding Readiness', icon: '📄', color: 'from-yellow-500 to-amber-500', description: '25+ documents for investors', link: '/funding' },
    { id: 'data-entry', name: 'Data Entry Automation', icon: '🏢', color: 'from-slate-500 to-gray-500', description: 'Paper to insights instantly', link: '/analyze/data-entry' },
    { id: 'expenses', name: 'Expense Management', icon: '💳', color: 'from-rose-500 to-red-500', description: 'Track spending, cut costs 30%+', link: '/analyze/expenses' },
  ]

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
          
          <nav className="hidden md:flex items-center gap-6">
            <Link href="/dashboard" className="text-white font-semibold">Dashboard</Link>
            <Link href="mailto:nsubugacollin@gmail.com" className="text-slate-400 hover:text-white transition-colors">Contact</Link>
            <a href="tel:+256705885118" className="text-slate-400 hover:text-white transition-colors">+256 705 885 118</a>
          </nav>
        </div>
      </header>

      {/* Main Content */}
      <main className="max-w-7xl mx-auto px-4 py-12">
        {/* Hero Section */}
        <div className="text-center mb-16">
          <h1 className="text-5xl md:text-7xl font-black mb-6 bg-gradient-to-r from-white via-blue-100 to-white bg-clip-text text-transparent">
            Command Deck
          </h1>
          <p className="text-xl text-slate-300 mb-8">
            Choose your intelligence domain and let CLARITY work its magic ✨
          </p>
          <div className="inline-block px-4 py-2 rounded-lg bg-green-500/20 border border-green-500/30 text-green-200 text-sm">
            <span className="inline-block w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse"></span>
            All Systems Operational
          </div>
        </div>

        {/* Domains Grid - Direct Launch (No Selection Panel) */}
        <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 mb-16">
          {domains.map((domain) => (
            <Link
              key={domain.id}
              href={domain.link || '/dashboard'}
              className="group relative p-6 rounded-2xl bg-slate-800/50 border border-slate-700/50 hover:border-blue-500/50 backdrop-blur-sm transition-all hover:transform hover:scale-105 hover:shadow-2xl text-left block"
            >
              {/* Gradient overlay */}
              <div className={`absolute inset-0 rounded-2xl bg-gradient-to-br ${domain.color} opacity-0 group-hover:opacity-10 transition-opacity`}></div>
              
              <div className="relative z-10">
                <div className="text-5xl mb-4">{domain.icon}</div>
                <h3 className="text-xl font-bold mb-2 text-white group-hover:text-blue-400 transition-colors">
                  {domain.name}
                </h3>
                <p className="text-slate-400 text-sm leading-relaxed">
                  {domain.description}
                </p>
                <div className="mt-4 text-amber-400 text-sm font-semibold opacity-0 group-hover:opacity-100 transition-opacity">
                  Launch →
                </div>
              </div>
            </Link>
          ))}
        </div>

        {/* Stats Section */}
        <div className="mt-16 grid grid-cols-2 md:grid-cols-4 gap-6">
          <div className="p-6 rounded-xl bg-slate-800/30 border border-white/10 text-center">
            <div className="text-3xl font-bold text-amber-400 mb-2">📧</div>
            <div className="text-slate-400 text-sm">Email Delivery</div>
          </div>
          <div className="p-6 rounded-xl bg-slate-800/30 border border-white/10 text-center">
            <div className="text-3xl font-bold text-blue-400 mb-2">11</div>
            <div className="text-slate-400 text-sm">Domains</div>
          </div>
          <div className="p-6 rounded-xl bg-slate-800/30 border border-white/10 text-center">
            <div className="text-3xl font-bold text-green-400 mb-2">99.9%</div>
            <div className="text-slate-400 text-sm">Uptime</div>
          </div>
          <div className="p-6 rounded-xl bg-slate-800/30 border border-white/10 text-center">
            <div className="text-3xl font-bold text-purple-400 mb-2">24/7</div>
            <div className="text-slate-400 text-sm">Available</div>
          </div>
        </div>

        {/* Contact CTA */}
        <div className="mt-16 p-8 rounded-2xl bg-gradient-to-r from-amber-500/10 to-amber-600/10 border border-amber-500/30 text-center">
          <h3 className="text-2xl font-bold text-white mb-4">
            Need Help or Want Enterprise Features?
          </h3>
          <p className="text-slate-300 mb-6">
            Contact Clarity Pearl for personalized support and custom solutions
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a
              href="mailto:nsubugacollin@gmail.com"
              className="px-6 py-3 bg-amber-500 hover:bg-amber-400 text-slate-900 font-bold rounded-xl transition-all"
            >
              📧 Email Us
            </a>
            <a
              href="tel:+256705885118"
              className="px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white font-semibold rounded-xl transition-colors"
            >
              📱 Call +256 705 885 118
            </a>
          </div>
        </div>
      </main>
    </div>
  )
}
