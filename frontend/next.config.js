/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  env: {
    NEXT_PUBLIC_API_URL: process.env.NEXT_PUBLIC_API_URL || 'https://veritas-engine-zae0.onrender.com',
  },
  experimental: {
    turbo: {
      root: __dirname,
    },
  },
}

module.exports = nextConfig
