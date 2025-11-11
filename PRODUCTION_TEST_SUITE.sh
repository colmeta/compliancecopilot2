#!/bin/bash

# ==============================================================================
# VERITAS ENGINE - PRODUCTION TEST SUITE
# Complete system verification for production deployment
# ==============================================================================

API_BASE="https://veritas-engine-zae0.onrender.com"

echo "=============================================="
echo "VERITAS ENGINE - PRODUCTION TEST SUITE"
echo "Testing ALL endpoints systematically"
echo "=============================================="
echo ""

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASS=0
FAIL=0

test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="$5"
    
    echo -n "Testing: $name... "
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s -o /dev/null -w "%{http_code}" "$API_BASE$endpoint")
    else
        response=$(curl -s -o /dev/null -w "%{http_code}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            "$API_BASE$endpoint")
    fi
    
    if [ "$response" == "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $response)"
        ((PASS++))
    else
        echo -e "${RED}❌ FAIL${NC} (Expected $expected_status, got $response)"
        ((FAIL++))
    fi
}

echo "=== CORE HEALTH CHECKS ==="
test_endpoint "Real AI Health" "GET" "/real/health" "" "200"
test_endpoint "Funding Health" "GET" "/funding/health" "" "200"
test_endpoint "Funding Health (alt)" "GET" "/real/funding/health" "" "200"
test_endpoint "Expense Health" "GET" "/expenses/health" "" "200"
test_endpoint "Test Status" "GET" "/test/status" "" "200"
echo ""

echo "=== DOMAIN ENDPOINTS ==="
test_endpoint "Real Domains" "GET" "/real/domains" "" "200"
test_endpoint "Instant Domains" "GET" "/instant/domains" "" "200"
test_endpoint "Quick Domains" "GET" "/quick/domains" "" "200"
echo ""

echo "=== AI ANALYSIS ENDPOINTS ==="

# Test Real AI Analysis (all 10 domains)
domains=("legal" "financial" "security" "healthcare" "data-science" "education" "proposals" "ngo" "data-entry" "expenses")

for domain in "${domains[@]}"; do
    data='{"directive":"Test analysis","domain":"'$domain'","document_content":"Test content"}'
    test_endpoint "Real AI - $domain" "POST" "/real/analyze" "$data" "200"
done
echo ""

echo "=== INSTANT ANALYSIS (Free Tier) ==="
test_endpoint "Instant Analyze - Legal" "POST" "/instant/analyze" \
    '{"directive":"Test","domain":"legal"}' "200"
test_endpoint "Instant Analyze - Financial" "POST" "/instant/analyze" \
    '{"directive":"Test","domain":"financial"}' "200"
echo ""

echo "=== FUNDING DOCUMENT ENDPOINTS ==="
test_endpoint "Funding Documents List" "GET" "/real/funding/documents" "" "200"
echo ""

echo "=== EXPENSE MANAGEMENT ==="
# Note: Receipt scanning requires multipart/form-data, tested separately
test_endpoint "Expense Summary" "GET" "/expenses/summary?user_id=test&days=30" "" "200"
echo ""

echo "=== BATCH PROCESSING ==="
test_endpoint "Batch Health" "GET" "/batch/health" "" "200"
echo ""

echo "=== DIAGNOSTICS ==="
test_endpoint "System Check" "GET" "/system/check" "" "200"
test_endpoint "Ferrari Diagnostics" "GET" "/ferrari/check" "" "200"
echo ""

echo "=============================================="
echo "TEST RESULTS"
echo "=============================================="
echo -e "${GREEN}PASSED: $PASS${NC}"
echo -e "${RED}FAILED: $FAIL${NC}"
echo "TOTAL:  $((PASS + FAIL))"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 ALL TESTS PASSED! Production ready!${NC}"
    exit 0
else
    echo -e "${RED}⚠️  Some tests failed. Review errors above.${NC}"
    exit 1
fi
