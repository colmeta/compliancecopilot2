#!/bin/bash

# 🏎️ FERRARI INSPECTION - COMPLETE SYSTEM TEST
# Real engineer testing - NO MERCY, FIND ALL BUGS

BACKEND_URL="https://veritas-engine-zae0.onrender.com"

echo "🏎️ FERRARI INSPECTION STARTING..."
echo "=================================================="
echo "Backend: $BACKEND_URL"
echo "Timestamp: $(date)"
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PASSED=0
FAILED=0
WARNINGS=0

test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local expected_status="$4"
    local data="$5"
    
    echo -n "Testing: $name... "
    
    if [ "$method" = "GET" ]; then
        response=$(curl -s -w "\n%{http_code}" "$BACKEND_URL$endpoint" 2>&1)
    else
        response=$(curl -s -w "\n%{http_code}" -X "$method" "$BACKEND_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data" 2>&1)
    fi
    
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | head -n-1)
    
    if [ "$http_code" = "$expected_status" ]; then
        echo -e "${GREEN}✅ PASS${NC} (HTTP $http_code)"
        echo "   Response: $(echo "$body" | head -c 100)..."
        ((PASSED++))
    else
        echo -e "${RED}❌ FAIL${NC} (Expected $expected_status, got $http_code)"
        echo "   Response: $body"
        ((FAILED++))
    fi
    echo ""
}

echo "=================================================="
echo "🧪 PHASE 1: CORE INFRASTRUCTURE TESTS"
echo "=================================================="
echo ""

# Test 1: Root endpoint
test_endpoint "Root Endpoint" "GET" "/" "200"

# Test 2: Health endpoints
test_endpoint "OCR Health" "GET" "/ocr/health" "503"  # Expected 503 if no engines
test_endpoint "Real AI Health" "GET" "/real/health" "200"
test_endpoint "V2 Funding Health" "GET" "/v2/funding/health" "200"
test_endpoint "Expense Health" "GET" "/expenses/health" "200"

echo "=================================================="
echo "🧪 PHASE 2: API ENDPOINT AVAILABILITY"
echo "=================================================="
echo ""

# Test document list
test_endpoint "Real Funding Documents List" "GET" "/real/funding/documents" "200"

# Test domain list
test_endpoint "Real AI Domains List" "GET" "/real/domains" "200"

# Test OCR status
test_endpoint "OCR Status" "GET" "/ocr/status" "200"

echo "=================================================="
echo "🧪 PHASE 3: EMAIL SYSTEM TEST"
echo "=================================================="
echo ""

test_endpoint "Email Config Check" "GET" "/test/email/config" "200"

echo "=================================================="
echo "📊 TEST RESULTS SUMMARY"
echo "=================================================="
echo ""
echo -e "${GREEN}✅ PASSED: $PASSED${NC}"
echo -e "${RED}❌ FAILED: $FAILED${NC}"
echo -e "${YELLOW}⚠️  WARNINGS: $WARNINGS${NC}"
echo ""

if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}🏎️ FERRARI IS READY TO RACE!${NC}"
    exit 0
else
    echo -e "${RED}🔧 FERRARI NEEDS REPAIRS!${NC}"
    exit 1
fi
