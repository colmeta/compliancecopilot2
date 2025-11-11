#!/bin/bash

###############################################################################
# CLARITY ENGINE MCP SERVER - INSTALLATION SCRIPT
###############################################################################

set -e

echo "🚀 Installing CLARITY Engine MCP Server..."
echo ""

# Check Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js not found. Please install Node.js 18+ first."
    echo "   Visit: https://nodejs.org"
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js version 18+ required (found v$NODE_VERSION)"
    exit 1
fi

echo "✅ Node.js $(node -v) found"
echo ""

# Install dependencies
echo "📦 Installing dependencies..."
cd "$(dirname "$0")"
npm install

echo ""
echo "✅ Dependencies installed"
echo ""

# Create .env if not exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file..."
    cp .env.example .env
    echo "✅ .env created (edit if needed)"
else
    echo "✅ .env already exists"
fi

echo ""
echo "🧪 Testing server..."
timeout 3s npm start 2>&1 | head -n 1 || true
echo ""

echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "✅ INSTALLATION COMPLETE!"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📋 Next Steps:"
echo ""
echo "1️⃣  Configure Claude Desktop:"
echo ""
echo "    macOS:"
echo "    Edit: ~/Library/Application Support/Claude/claude_desktop_config.json"
echo ""
echo "    Add this configuration:"
echo ""
cat << 'EOF'
    {
      "mcpServers": {
        "clarity-engine": {
          "command": "node",
          "args": ["ABSOLUTE_PATH_TO/mcp-server/server.js"],
          "env": {
            "CLARITY_API_URL": "https://veritas-engine-zae0.onrender.com"
          }
        }
      }
    }
EOF
echo ""
echo "    Replace ABSOLUTE_PATH_TO with: $(pwd)"
echo ""
echo "2️⃣  Restart Claude Desktop"
echo ""
echo "3️⃣  Look for 🔧 icon in Claude - you should see 11 CLARITY tools"
echo ""
echo "4️⃣  Try it:"
echo '    "Use the list_domains tool to show me available intelligence domains"'
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 Full documentation: ./README.md"
echo "🔧 Example configs: ./config-examples/"
echo ""
