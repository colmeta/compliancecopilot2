# MCP Server Deployment Checklist

Use this checklist to deploy CLARITY MCP Server to your team or clients.

---

## ✅ Pre-Deployment Checks

### 1. System Requirements
- [ ] Node.js 18+ installed (`node --version`)
- [ ] npm available (`npm --version`)
- [ ] Internet connection (for API calls)
- [ ] Claude Desktop or Cursor IDE installed

### 2. Code Quality
- [x] Server starts without errors
- [x] All dependencies installed
- [x] Environment variables documented
- [x] Error handling implemented
- [x] Documentation complete

### 3. API Connectivity
- [ ] Backend API accessible: `curl https://veritas-engine-zae0.onrender.com/health`
- [ ] API key configured (if needed)
- [ ] Rate limits understood
- [ ] Error responses handled

---

## 📦 Installation Steps

### For End Users (Claude Desktop)

**Step 1: Download Repository**
```bash
git clone <repository-url>
cd workspace/mcp-server
```

**Step 2: Install Dependencies**
```bash
./install.sh
# Or manually: npm install && cp .env.example .env
```

**Step 3: Configure Claude Desktop**

**macOS:**
```bash
# Edit config file
nano ~/Library/Application\ Support/Claude/claude_desktop_config.json

# Add CLARITY configuration (see below)
```

**Windows:**
```powershell
# Edit config file
notepad %APPDATA%\Claude\claude_desktop_config.json

# Add CLARITY configuration (see below)
```

**Configuration to add:**
```json
{
  "mcpServers": {
    "clarity-engine": {
      "command": "node",
      "args": ["/ABSOLUTE/PATH/TO/mcp-server/server.js"],
      "env": {
        "CLARITY_API_URL": "https://veritas-engine-zae0.onrender.com"
      }
    }
  }
}
```

**Step 4: Restart Claude Desktop**
- Quit Claude completely
- Reopen
- Look for 🔧 icon (tools available)
- Should see 11 CLARITY tools

**Step 5: Test**
```
In Claude Desktop, say:
"Use the list_domains tool to show me available intelligence domains"
```

---

### For Developers (Cursor IDE)

**Step 1-2:** Same as above

**Step 3: Configure Cursor**
```bash
# Create or edit .cursor/mcp_config.json in workspace root
nano .cursor/mcp_config.json
```

Add:
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

**Step 4:** Restart Cursor

**Step 5:** Test in Cursor AI chat

---

## 🧪 Testing Checklist

### Automated Tests
```bash
cd mcp-server
./test-server.sh
```

Expected output:
```
✅ Server starts
✅ API reachable (or warning if hibernating)
✅ Node.js 18+
```

### Manual Testing in Claude

Test each tool category:

- [ ] **Legal:** `Use analyze_legal tool on a sample contract`
- [ ] **Financial:** `Use analyze_financial tool on budget data`
- [ ] **Security:** `Use analyze_security tool on security policy`
- [ ] **Healthcare:** `Use analyze_healthcare tool on HIPAA docs`
- [ ] **Data Science:** `Use analyze_data tool on sales data`
- [ ] **Proposals:** `Use analyze_proposal tool on RFP`
- [ ] **NGO:** `Use analyze_ngo tool for grant writing`
- [ ] **Expenses:** `Use analyze_expenses tool on receipts`
- [ ] **Discovery:** `Use list_domains tool`
- [ ] **Health:** `Use check_health tool`
- [ ] **Funding:** `Use generate_funding_documents tool`

### Error Handling Tests

- [ ] Test with API offline (should show clear error)
- [ ] Test with invalid input (should handle gracefully)
- [ ] Test with empty fields (should prompt for required)

---

## 🚨 Common Issues & Solutions

### Issue: Tools not showing in Claude

**Diagnosis:**
```bash
# Check config syntax
cat ~/Library/Application\ Support/Claude/claude_desktop_config.json | jq .
# Should parse without errors
```

**Solutions:**
1. Ensure absolute path to server.js
2. Check JSON syntax (no trailing commas)
3. Restart Claude completely
4. Check Claude logs: `~/Library/Logs/Claude/mcp*.log`

---

### Issue: "Command not found" error

**Diagnosis:**
```bash
which node
# Should show Node.js path
```

**Solutions:**
1. Install Node.js 18+
2. Add Node.js to PATH
3. Use full path to node in config:
   ```json
   "command": "/usr/local/bin/node"
   ```

---

### Issue: API connection timeout

**Diagnosis:**
```bash
curl -v https://veritas-engine-zae0.onrender.com/health
# Check response time
```

**Solutions:**
1. Wait 30 seconds (Render hibernation)
2. Check internet connection
3. Verify API URL in .env
4. Check for firewall blocking

---

### Issue: "Missing dependencies" error

**Solution:**
```bash
cd mcp-server
rm -rf node_modules package-lock.json
npm install
```

---

## 📊 Monitoring

### Health Checks

**Daily:**
```bash
# Check API status
curl https://veritas-engine-zae0.onrender.com/health

# Test MCP server
cd mcp-server && npm start
# Should output: "CLARITY Engine MCP server running"
```

**Weekly:**
- Test all 11 tools
- Review Claude/Cursor logs
- Check for dependency updates: `npm outdated`

**Monthly:**
- Update dependencies: `npm update`
- Review API usage/limits
- Check for MCP SDK updates

---

## 🔒 Security Considerations

### API Keys
- [ ] Store API keys in .env (never commit)
- [ ] Use separate keys for dev/prod
- [ ] Rotate keys regularly
- [ ] Monitor API usage

### Access Control
- [ ] Limit who can modify server.js
- [ ] Review Claude Desktop configs
- [ ] Monitor tool usage
- [ ] Audit logs regularly

### Data Privacy
- [ ] No sensitive data in logs
- [ ] HTTPS for all API calls
- [ ] Comply with data retention policies
- [ ] Document data flows

---

## 📈 Performance Optimization

### For Faster Response Times

1. **Wake API before use:**
   ```bash
   curl https://veritas-engine-zae0.onrender.com/health
   # Wait 30s, then use tools
   ```

2. **Upgrade Render tier:**
   - Free tier: 15min hibernation
   - Paid tier: Always on
   - Recommendation: $7/month for production

3. **Use UptimeRobot:**
   - Free service
   - Pings every 5 minutes
   - Prevents hibernation

4. **Cache results:**
   - Add caching layer in server.js
   - Store frequent queries
   - Reduce API calls

---

## 🎯 Success Metrics

Track these to measure adoption:

- **Installation Time:** Target < 5 minutes
- **First Success:** Tool works within 10 minutes
- **Daily Active Users:** Number using tools daily
- **Tool Usage:** Which tools used most
- **Error Rate:** Should be < 5%
- **Response Time:** Average < 3 seconds

---

## 📝 User Onboarding

### For Non-Technical Users

**Email Template:**
```
Subject: New AI Tools Available in Claude Desktop

Hi [Name],

We've added 11 new AI-powered tools to your Claude Desktop:

• Legal contract analysis
• Financial budget review
• Security compliance audits
• Healthcare HIPAA checks
• Data trend analysis
• Proposal optimization
• Grant writing assistance
• Expense tracking
• Funding document generation
• And more!

SETUP (5 minutes):
1. Download: [link to repository]
2. Run: ./install.sh
3. Configure: [link to guide]
4. Restart Claude Desktop

FIRST TEST:
In Claude, say: "Use the list_domains tool"

HELP:
[Link to documentation]
[Contact: your-email]

Questions? Reply to this email!
```

---

## 🚀 Rollout Plan

### Phase 1: Internal Testing (Week 1)
- [ ] Deploy to 3-5 team members
- [ ] Collect feedback
- [ ] Fix issues
- [ ] Document common problems

### Phase 2: Beta Release (Week 2)
- [ ] Deploy to 10-20 users
- [ ] Monitor usage patterns
- [ ] Optimize performance
- [ ] Update documentation

### Phase 3: General Availability (Week 3+)
- [ ] Deploy to all users
- [ ] Announce publicly
- [ ] Provide training
- [ ] Ongoing support

---

## 📞 Support Resources

### Documentation
- Installation: `README.md`
- Usage Examples: `USAGE_EXAMPLES.md`
- Troubleshooting: This checklist
- API Docs: https://veritas-engine-zae0.onrender.com

### Support Channels
- GitHub Issues: [repository-url]/issues
- Email: [support-email]
- Slack: #clarity-support
- Office Hours: [schedule]

### Training Materials
- Video Tutorial: [link]
- Quick Start Guide: [link]
- Example Prompts: `USAGE_EXAMPLES.md`
- FAQ: [link]

---

## ✅ Final Sign-Off

Before considering deployment complete:

- [ ] All automated tests passing
- [ ] Manual testing complete (all 11 tools)
- [ ] Documentation reviewed
- [ ] Support channels ready
- [ ] Monitoring configured
- [ ] Rollback plan documented
- [ ] Success metrics defined
- [ ] Team trained

**Deployed by:** ________________

**Date:** ________________

**Version:** 1.0.0

**Notes:**
_________________________________
_________________________________
_________________________________

---

**Ready for production deployment!** 🚀
