import type { Metadata } from 'next'
import { Inter } from 'next/font/google'
import Script from 'next/script'
import './globals.css'

const inter = Inter({ subsets: ['latin'] })

export const metadata: Metadata = {
  title: 'CLARITY Engine - Fortune 50 AI Intelligence Platform',
  description: 'Enterprise-grade AI intelligence for Legal, Financial, Compliance, Healthcare, and more. Save $249K-$800K per year.',
  keywords: 'AI, Enterprise, Legal Intelligence, Financial Analysis, Compliance, Healthcare, Business Intelligence',
  authors: [{ name: 'Clarity Pearl' }],
  creator: 'Clarity Pearl',
  publisher: 'Clarity Pearl',
  manifest: '/manifest.json',
  themeColor: '#f59e0b',
  viewport: {
    width: 'device-width',
    initialScale: 1,
    maximumScale: 1,
    userScalable: false,
  },
  appleWebApp: {
    capable: true,
    statusBarStyle: 'black-translucent',
    title: 'CLARITY Engine',
  },
  openGraph: {
    type: 'website',
    locale: 'en_US',
    url: 'https://clarity-engine-auto.vercel.app',
    title: 'CLARITY Engine - Fortune 50 AI Intelligence Platform',
    description: 'Save $249K-$800K annually with AI-powered enterprise intelligence',
    siteName: 'CLARITY Engine',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'CLARITY Engine - Fortune 50 AI Intelligence',
    description: 'Enterprise-grade AI intelligence platform',
  },
  icons: {
    icon: [
      { url: '/icon-192.png', sizes: '192x192', type: 'image/png' },
      { url: '/icon-512.png', sizes: '512x512', type: 'image/png' },
    ],
    apple: [
      { url: '/icon-192.png', sizes: '192x192', type: 'image/png' },
    ],
  },
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <head>
        <link rel="manifest" href="/manifest.json" />
        <link rel="icon" type="image/svg+xml" href="/icon.svg" />
        <link rel="apple-touch-icon" href="/icon.svg" />
        <meta name="mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-capable" content="yes" />
        <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent" />
        <meta name="apple-mobile-web-app-title" content="CLARITY" />
        <meta name="application-name" content="CLARITY Engine" />
        <meta name="msapplication-TileColor" content="#0f172a" />
        <meta name="msapplication-tap-highlight" content="no" />
      </head>
      <body className={inter.className}>
        {children}
        <Script src="/register-sw.js" strategy="afterInteractive" />
      </body>
    </html>
  )
}
