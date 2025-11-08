# CLARITY Engine MCP Server

**Model Context Protocol (MCP) server for CLARITY Engine**

Allows Claude Desktop, Cursor, and other AI tools to directly access CLARITY's 10 intelligence domains.

---

## 🚀 Quick Start

### 1. Install Dependencies

```bash
cd mcp-server
npm install
```

### 2. Configure Environment

Create `.env` file:

```bash
CLARITY_API_URL=https://veritas-engine-zae0.onrender.com
CLARITY_API_KEY=your_api_key_here  # Optional
```

### 3. Test Locally

```bash
npm start
```

---

## 🔧 Integration with Claude Desktop

### macOS

Edit `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "clarity-engine": {
      "command": "node",
      "args": ["/path/to/workspace/mcp-server/server.js"],
      "env": {
        "CLARITY_API_URL": "https://veritas-engine-zae0.onrender.com"
      }
    }
  }
}
```

### Windows

Edit `%APPDATA%\Claude\claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "clarity-engine": {
      "command": "node",
      "args": ["C:\\path\\to\\workspace\\mcp-server\\server.js"],
      "env": {
        "CLARITY_API_URL": "https://veritas-engine-zae0.onrender.com"
      }
    }
  }
}
```

### Linux

Edit `~/.config/Claude/claude_desktop_config.json` (same as macOS)

---

## 🎯 Available Tools

Once configured, you can use these tools in Claude Desktop:

### 1. **analyze_legal**
```
Analyze legal documents for compliance, risks, and liability clauses
```

### 2. **analyze_financial**
```
Analyze financial statements for anomalies, trends, and risks
```

### 3. **analyze_security**
```
Audit security policies and SOC2 compliance
```

### 4. **analyze_healthcare**
```
HIPAA compliance and clinical protocol review
```

### 5. **analyze_data**
```
Statistical analysis and predictive modeling
```

### 6. **analyze_proposal**
```
RFP response optimization and bid analysis
```

### 7. **analyze_ngo**
```
Grant writing and impact assessment
```

### 8. **analyze_expenses**
```
Expense analysis and cost optimization
```

### 9. **list_domains**
```
List all available CLARITY intelligence domains
```

### 10. **generate_funding_documents**
```
Generate complete funding document packages
```

### 11. **check_health**
```
Check CLARITY engine status
```

---

## 💡 Usage Examples

### In Claude Desktop:

**Example 1: Legal Analysis**
```
Use the analyze_legal tool to review this contract for liability issues:
[paste contract text]
```

**Example 2: Financial Analysis**
```
Use the analyze_financial tool to find anomalies in this budget:
[paste financial data]
```

**Example 3: List Capabilities**
```
Use the list_domains tool to show me all available intelligence domains
```

**Example 4: Funding Documents**
```
Use the generate_funding_documents tool to create a funding package for:
- Company: TechStart AI
- Description: AI-powered code review platform
- Industry: Software/SaaS
- Funding Goal: $2M seed round
```

---

## 🔧 Integration with Cursor IDE

Add to your Cursor settings (`.cursor/mcp_config.json`):

```json
{
  "mcpServers": {
    "clarity-engine": {
      "command": "node",
      "args": ["./mcp-server/server.js"],
      "env": {
        "CLARITY_API_URL": "https://veritas-engine-zae0.onrender.com"
      }
    }
  }
}
```

---

## 🧪 Testing

Test the MCP server manually:

```bash
# Start server
npm start

# In another terminal, test with MCP client
npx @modelcontextprotocol/inspector node server.js
```

---

## 🏗️ Architecture

```
┌─────────────────┐
│  Claude Desktop │
│  or Cursor IDE  │
└────────┬────────┘
         │ MCP Protocol
         │
┌────────▼────────┐
│  MCP Server     │
│  (This Server)  │
└────────┬────────┘
         │ REST API
         │
┌────────▼────────┐
│ CLARITY Engine  │
│  (Backend API)  │
└─────────────────┘
```

---

## 📝 Configuration Options

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `CLARITY_API_URL` | No | `https://veritas-engine-zae0.onrender.com` | CLARITY API base URL |
| `CLARITY_API_KEY` | No | None | API key for authenticated requests |

---

## 🚨 Troubleshooting

### MCP Server Not Showing in Claude

1. **Check config file path**
   - macOS: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - Make sure path to `server.js` is absolute

2. **Check Node.js version**
   ```bash
   node --version  # Should be >= 18.0.0
   ```

3. **Test server manually**
   ```bash
   node server.js
   # Should output: "CLARITY Engine MCP server running on stdio"
   ```

4. **Check Claude logs**
   - macOS: `~/Library/Logs/Claude/mcp*.log`
   - Look for error messages

### API Connection Issues

1. **Server hibernating**
   - Visit https://veritas-engine-zae0.onrender.com/health
   - Wait 30 seconds for server to wake

2. **API key issues**
   - Remove `CLARITY_API_KEY` from env if not needed
   - Most endpoints work without authentication

---

## 🎯 Benefits

**For Developers:**
- Access CLARITY from within your IDE (Cursor)
- No need to switch contexts
- AI-powered code review and analysis

**For Business Users:**
- Access CLARITY from Claude Desktop
- Natural language interface
- All 10 intelligence domains available

**For Everyone:**
- Faster workflows
- Better AI assistance
- Seamless integration

---

## 📚 Learn More

- **MCP Protocol:** https://modelcontextprotocol.io
- **CLARITY Engine API:** https://veritas-engine-zae0.onrender.com
- **Claude Desktop:** https://claude.ai/download

---

## 🤝 Support

Issues? Questions?

1. Check server logs: `npm start` (watch for errors)
2. Test API directly: `curl https://veritas-engine-zae0.onrender.com/real/health`
3. Verify Node.js version: `node --version`

---

**Built with ❤️ for seamless AI integration**
