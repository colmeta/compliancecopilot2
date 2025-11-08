#!/bin/bash

###############################################################################
# CLARITY MCP SERVER - TEST SCRIPT
###############################################################################

echo "🧪 Testing CLARITY MCP Server..."
echo ""

cd "$(dirname "$0")"

# Check if node_modules exists
if [ ! -d "node_modules" ]; then
    echo "❌ Dependencies not installed. Run: npm install"
    exit 1
fi

# Check environment
if [ ! -f ".env" ]; then
    echo "⚠️  No .env file found. Using defaults."
    export CLARITY_API_URL="https://veritas-engine-zae0.onrender.com"
fi

echo "📍 API URL: ${CLARITY_API_URL:-https://veritas-engine-zae0.onrender.com}"
echo ""

# Test 1: Server starts
echo "Test 1: Server startup..."
timeout 3s npm start 2>&1 | grep -q "CLARITY Engine MCP server running" && echo "✅ Server starts" || echo "❌ Server failed to start"

# Test 2: Check API connectivity
echo "Test 2: API connectivity..."
curl -s "${CLARITY_API_URL:-https://veritas-engine-zae0.onrender.com}/health" > /dev/null && echo "✅ API reachable" || echo "⚠️  API unreachable (may be hibernating)"

# Test 3: Node version
echo "Test 3: Node.js version..."
NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -ge 18 ]; then
    echo "✅ Node.js $(node -v)"
else
    echo "❌ Node.js version too old (need 18+, have $(node -v))"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "🎯 Manual Test:"
echo ""
echo "Run: npm start"
echo ""
echo "You should see: 'CLARITY Engine MCP server running on stdio'"
echo ""
echo "To test with MCP Inspector:"
echo "npx @modelcontextprotocol/inspector node server.js"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
