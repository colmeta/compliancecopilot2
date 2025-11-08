# CLARITY MCP Server - Usage Examples

Real-world examples of using CLARITY Engine through the MCP server in Claude Desktop.

---

## 🎯 Legal Intelligence

### Contract Review

**Prompt in Claude Desktop:**
```
Use the analyze_legal tool to review this software license agreement for any concerning clauses:

[Software License Agreement]

This Agreement is made between Company X ("Licensor") and Customer ("Licensee").

1. GRANT OF LICENSE
   Licensor grants Licensee a non-exclusive, non-transferable license...

2. LIABILITY
   TO THE MAXIMUM EXTENT PERMITTED BY LAW, LICENSOR SHALL NOT BE LIABLE
   FOR ANY INDIRECT, INCIDENTAL, SPECIAL, OR CONSEQUENTIAL DAMAGES...

3. TERMINATION
   This license may be terminated immediately without notice if...

4. DATA USAGE
   Licensee agrees that all data processed through the software becomes
   property of Licensor for improvement purposes...
```

**Expected Output:**
```
# LEGAL INTELLIGENCE ANALYSIS

**Directive:** Review for concerning clauses

## Summary
Critical issues identified in sections 2, 3, and 4 requiring immediate attention.

## Key Findings
1. 🔴 CRITICAL: Section 4 (Data Usage) - Grants Licensor ownership of YOUR data
2. ⚠️  HIGH: Section 2 (Liability) - Extremely broad liability waiver
3. ⚠️  MEDIUM: Section 3 (Termination) - No cure period before termination

## Recommendations
1. Negotiate removal of Section 4 data ownership clause
2. Request liability cap equal to fees paid
3. Add 30-day cure period for non-material breaches
```

---

## 💰 Financial Intelligence

### Budget Analysis

**Prompt:**
```
Use the analyze_financial tool to find cost-saving opportunities in this Q1 budget:

Department: Marketing
Q1 Budget: $250,000

- Google Ads: $85,000
- LinkedIn Ads: $45,000
- Content Marketing: $35,000
- Events & Conferences: $40,000
- Software Tools: $25,000
  - HubSpot: $8,000
  - Salesforce: $12,000
  - Various SaaS: $5,000
- Miscellaneous: $20,000
```

**Expected Output:**
```
# FINANCIAL INTELLIGENCE ANALYSIS

## Summary
Identified $47,000 in potential savings (18.8% reduction) through optimization.

## Key Findings
1. Ad spend (52% of budget) shows opportunity for efficiency
2. Software overlap detected - HubSpot + Salesforce
3. "Miscellaneous" category too large (8% of budget)

## Recommendations
1. 💰 SAVE $15K: Consolidate HubSpot/Salesforce (choose one)
2. 💰 SAVE $17K: Reduce Google Ads by 20%, improve targeting
3. 💰 SAVE $10K: Negotiate annual vs monthly SaaS contracts
4. 💰 SAVE $5K: Eliminate/categorize miscellaneous spending
```

---

## 🔒 Security Intelligence

### SOC2 Compliance Check

**Prompt:**
```
Use the analyze_security tool to audit our security policy for SOC2 readiness:

SECURITY POLICY v1.0

Access Control:
- Password requirements: 8+ characters
- MFA: Optional for employees
- Admin accounts: Shared among 3 team members
- Password rotation: Recommended annually

Data Handling:
- Customer data stored in MongoDB
- Backups: Weekly to local server
- Encryption: SSL in transit
- No formal data classification
```

**Expected Output:**
```
# SECURITY INTELLIGENCE ANALYSIS

## Summary
🚨 NOT SOC2 READY - Multiple critical compliance gaps identified.

## Key Findings
1. 🔴 CRITICAL: Shared admin credentials (SOC2 violation)
2. 🔴 CRITICAL: MFA optional (required for SOC2 Type 2)
3. 🔴 HIGH: Local backups only (no disaster recovery)
4. ⚠️  MEDIUM: 8-char passwords insufficient (need 12+)
5. ⚠️  MEDIUM: Missing data classification system

## Recommendations
1. Implement individual admin accounts (required)
2. Enforce MFA for ALL accounts (required)
3. Add off-site backup location (required)
4. Increase password requirement to 12+ characters
5. Document data classification policy
6. Implement 90-day password rotation policy
```

---

## 🏥 Healthcare Intelligence

### HIPAA Compliance Review

**Prompt:**
```
Use the analyze_healthcare tool to check our patient portal for HIPAA compliance:

Feature: Patient Portal
- Patients can view medical records
- Authentication: Username + password (6 chars minimum)
- Session timeout: 60 minutes
- Data transmission: HTTPS
- Logs: Access logs kept for 3 months
- User can email records to themselves
- No audit trail for who accessed what
```

**Expected Output:**
```
# HEALTHCARE INTELLIGENCE ANALYSIS

## Summary
⚠️  HIPAA VIOLATIONS DETECTED - Immediate remediation required.

## Key Findings
1. 🔴 VIOLATION: 3-month log retention (HIPAA requires 6 years)
2. 🔴 VIOLATION: No audit trail for PHI access
3. 🔴 VIOLATION: Email records feature (unsecured transmission)
4. ⚠️  HIGH: 6-char password too weak for PHI
5. ⚠️  MEDIUM: 60-min session timeout too long

## Recommendations
1. Extend log retention to 6 years (REQUIRED)
2. Implement comprehensive audit logging (REQUIRED)
3. Remove email feature or add encryption (REQUIRED)
4. Increase password requirement to 12+ characters
5. Reduce session timeout to 15 minutes
6. Add automatic logout on inactivity
```

---

## 📊 Data Science

### Sales Trend Analysis

**Prompt:**
```
Use the analyze_data tool to find trends in our Q1 sales data:

Sales Data - Q1 2024:
Week 1: $45,000
Week 2: $48,000
Week 3: $52,000
Week 4: $47,000
Week 5: $51,000
Week 6: $55,000
Week 7: $58,000
Week 8: $62,000
Week 9: $59,000
Week 10: $65,000
Week 11: $68,000
Week 12: $71,000

Team Performance:
Team A: $312,000 (6 reps)
Team B: $268,000 (5 reps)
Team C: $156,000 (3 reps)
```

**Expected Output:**
```
# DATA SCIENCE ANALYSIS

## Summary
Strong upward trend with 58% growth over 12 weeks. Team B shows highest efficiency.

## Key Findings
1. 📈 Revenue growing at ~4.8% per week
2. 🏆 Team B most efficient: $53.6K per rep
3. ⚠️  Team C underperforming: $52K per rep
4. 📊 Acceleration in weeks 7-12 (demand surge?)
5. 💡 Week 4 dip suggests mid-month challenge

## Recommendations
1. Study Team B's methodology - apply to Teams A & C
2. Investigate Week 4 pattern (recurring monthly issue?)
3. Q2 projection: $850K (based on current trend)
4. Consider adding 2 reps to Team B (highest ROI)
5. Analyze what changed in Week 7 (momentum shift)
```

---

## 📝 Proposal Intelligence

### RFP Response Check

**Prompt:**
```
Use the analyze_proposal tool to optimize our RFP response:

RFP: City of Springfield - Traffic Management System

Requirements:
✓ Real-time traffic monitoring
✓ Integration with existing cameras
✓ 5-year warranty required
✓ Must be deployed within 6 months
✓ Local support team required
✓ SOC2 Type 2 certified
✓ Budget: $2.5M

Our Response:
- Solution: SmartTraffic AI Platform
- Price: $2.8M
- Timeline: 8 months deployment
- Warranty: 3 years standard, 5 years for additional $200K
- Support: Remote team with 24/7 phone
- Certification: SOC2 Type 1 (Type 2 in progress)
```

**Expected Output:**
```
# PROPOSAL INTELLIGENCE ANALYSIS

## Summary
🚨 NON-COMPLIANT - Response fails 4 of 6 mandatory requirements.

## Key Findings
1. ❌ Price: Over budget by $300K (11% over)
2. ❌ Timeline: 2 months late (33% delay)
3. ❌ Warranty: Non-compliant (requires add-on)
4. ❌ Certification: Type 1 vs required Type 2
5. ⚠️  Support: Remote vs required local team
6. ✅ Technical solution: Meets requirements

## Recommendations
1. 💰 Reduce price to $2.5M or below (CRITICAL)
2. ⏱️  Commit to 6-month deployment (CRITICAL)
3. 🛡️  Include 5-year warranty in base price (CRITICAL)
4. 📜 Wait to submit until SOC2 Type 2 obtained (CRITICAL)
5. 🤝 Establish local support presence
6. Alternative: Request RFP amendment for timeline/price
```

---

## 🌍 NGO & Impact

### Grant Proposal Assistance

**Prompt:**
```
Use the analyze_ngo tool to create a grant proposal for:

Organization: Clean Water Initiative
Program: Rural Well Drilling Project
Target: 50 villages in Uganda
Budget Needed: $500,000
Grant: Gates Foundation - Water Access Grant
Impact: 25,000 people gain clean water access
Timeline: 18 months
```

**Expected Output:**
```
# NGO IMPACT ANALYSIS

## Grant Proposal Framework

### Executive Summary
Clean Water Initiative seeks $500K to deliver clean water to 25,000 people across 50 Ugandan villages through sustainable well-drilling program.

### Problem Statement
- Current situation: 25,000 people walk 3+ hours daily for water
- Health impact: 40% child mortality from waterborne diseases
- Economic impact: Women spend 6 hours/day on water collection

### Proposed Solution
- Drill 50 community wells (1 per village)
- Train local maintenance teams
- Implement water quality monitoring

### Budget Breakdown
- Well drilling: $350,000 ($7K per well)
- Equipment & materials: $75,000
- Training programs: $40,000
- Monitoring & evaluation: $25,000
- Administration: $10,000

### Expected Impact
- 25,000 people with clean water access
- 90% reduction in waterborne illness
- 6 hours/day saved per household
- $1.2M annual economic benefit (time savings)
- ROI: $2.40 per $1 invested

### Success Metrics
- Wells operational: Target 95% uptime
- Water quality tests: Monthly monitoring
- Community satisfaction: Quarterly surveys
- Health outcomes: Baseline + 12-month comparison

### Sustainability Plan
- Local maintenance teams trained
- Community contribution: 10% ongoing costs
- Partnership with Ministry of Water
- 10-year well lifespan
```

---

## 💳 Expense Management

### Receipt Analysis

**Prompt:**
```
Use the analyze_expenses tool to categorize and find savings in these expenses:

January 2024 Expenses:
- Starbucks (daily): $180
- Uber rides: $340
- AWS hosting: $1,250
- Office supplies: $89
- Client dinners: $560
- SaaS subscriptions: $420
- Conference ticket: $899
- Hotel (conference): $450
```

**Expected Output:**
```
# EXPENSE ANALYSIS

## Summary
Total: $4,188 | Savings opportunity: $912 (21.8%)

## Categorization
Business Essential: $2,719 (65%)
- AWS hosting: $1,250
- Conference: $1,349
- Office supplies: $89

Client Development: $560 (13%)
- Client dinners: $560

Potentially Reducible: $909 (22%)
- Coffee: $180
- Transport: $340
- SaaS: $420

## Savings Opportunities
1. ☕ Coffee: $120/mo savings
   - Bring coffee from home
   - Estimated savings: $1,440/year

2. 🚗 Transport: $200/mo savings
   - Monthly Uber pass: $140 vs $340 spent
   - Estimated savings: $2,400/year

3. 💻 SaaS: $150/mo savings
   - Audit subscriptions (likely unused tools)
   - Annual billing: Save 20%
   - Estimated savings: $1,800/year

4. 🏨 Conference hotel: $200 savings
   - Book earlier (conference hotel rate: $250)
   - Per conference savings

**Total Annual Savings Potential: $5,640**
```

---

## 🚀 Quick Commands

### Check Status
```
Use the check_health tool to see if CLARITY is ready
```

### List All Capabilities
```
Use the list_domains tool to show me what CLARITY can do
```

### Generate Funding Package
```
Use the generate_funding_documents tool for:
Company: AI Assistant Startup
Description: AI-powered customer service platform
Industry: SaaS
Funding Goal: $2M seed round
```

---

## 💡 Tips for Best Results

1. **Be specific in directives**
   - ❌ "Analyze this contract"
   - ✅ "Find liability clauses and termination risks in this contract"

2. **Provide context**
   - Include relevant background
   - Mention your industry/use case
   - State your specific concerns

3. **Use structured data**
   - Format financial data clearly
   - Use bullet points for lists
   - Label sections clearly

4. **Follow up**
   - Ask clarifying questions
   - Request deeper analysis on findings
   - Get specific recommendations

---

**Ready to use CLARITY in Claude Desktop? Try any of these examples!**
