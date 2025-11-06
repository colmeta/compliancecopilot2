#!/bin/bash
# ==============================================================================
# TEST ALL DOMAINS - Complete Backend Test Script
# ==============================================================================

BACKEND_URL="https://veritas-engine-zae0.onrender.com"
echo "🧪 Testing CLARITY Engine Backend: $BACKEND_URL"
echo "=================================================="
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Test counter
PASSED=0
FAILED=0

# ==============================================================================
# Test Function
# ==============================================================================
test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected="$5"
    
    echo -n "Testing $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s "$BACKEND_URL$endpoint" 2>&1)
    else
        response=$(curl -s -X POST "$BACKEND_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>&1)
    fi
    
    if echo "$response" | grep -q "$expected"; then
        echo -e "${GREEN}✅ PASSED${NC}"
        ((PASSED++))
    else
        echo -e "${RED}❌ FAILED${NC}"
        echo "   Expected: $expected"
        echo "   Got: $response"
        ((FAILED++))
    fi
}

# ==============================================================================
# 1. Health Checks
# ==============================================================================
echo "1️⃣  HEALTH CHECKS"
echo "-------------------"

test_endpoint \
    "Backend Health" \
    "GET" \
    "/instant/health" \
    "" \
    "healthy"

test_endpoint \
    "Domains List" \
    "GET" \
    "/instant/domains" \
    "" \
    "total"

echo ""

# ==============================================================================
# 2. Test All 10 Domains
# ==============================================================================
echo "2️⃣  DOMAIN ANALYSIS TESTS"
echo "-------------------------"

# Legal
test_endpoint \
    "Legal Analysis" \
    "POST" \
    "/instant/analyze" \
    '{"directive": "Review contract", "domain": "legal"}' \
    "Legal Intelligence Analysis"

# Financial
test_endpoint \
    "Financial Analysis" \
    "POST" \
    "/instant/analyze" \
    '{"directive": "Analyze expenses", "domain": "financial"}' \
    "Financial Intelligence Analysis"

# Security
test_endpoint \
    "Security Analysis" \
    "POST" \
    "/instant/analyze" \
    '{"directive": "Security audit", "domain": "security"}' \
    "Security Intelligence Audit"

# Healthcare
test_endpoint \
    "Healthcare Analysis" \
    "POST" \
    "/instant/analyze" \
    '{"directive": "Review patient data", "domain": "healthcare"}' \
    "Healthcare Intelligence Review"

# Data Science
test_endpoint \
    "Data Science Analysis" \
    "POST" \
    "/instant/analyze" \
    '{"directive": "Analyze dataset", "domain": "data-science"}' \
    "Data Science Analysis"

# Education
test_endpoint \
    "Education Analysis" \
    "POST" \
    "/instant/analyze" \
    '{"directive": "Curriculum review", "domain": "education"}' \
    "Education Intelligence Report"

# Proposals
test_endpoint \
    "Proposal Analysis" \
    "POST" \
    "/instant/analyze" \
    '{"directive": "Draft proposal", "domain": "proposals"}' \
    "Proposal Intelligence Draft"

# NGO
test_endpoint \
    "NGO Analysis" \
    "POST" \
    "/instant/analyze" \
    '{"directive": "Impact assessment", "domain": "ngo"}' \
    "NGO Impact Assessment"

# Data Entry
test_endpoint \
    "Data Entry Analysis" \
    "POST" \
    "/instant/analyze" \
    '{"directive": "Extract data", "domain": "data-entry"}' \
    "Data Entry Automation"

# Expenses
test_endpoint \
    "Expense Analysis" \
    "POST" \
    "/instant/analyze" \
    '{"directive": "Categorize expenses", "domain": "expenses"}' \
    "Expense Management Analysis"

echo ""

# ==============================================================================
# 3. Summary
# ==============================================================================
echo "=================================================="
echo "📊 TEST SUMMARY"
echo "=================================================="
echo -e "${GREEN}✅ Passed: $PASSED${NC}"
echo -e "${RED}❌ Failed: $FAILED${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! Backend is fully operational!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Check the output above.${NC}"
    exit 1
fi
