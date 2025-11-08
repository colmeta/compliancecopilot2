#!/bin/bash

# ==============================================================================
# CEO A/B TESTING SUITE - COMPREHENSIVE MARKET READINESS ASSESSMENT
# Testing every endpoint, measuring performance, identifying issues
# ==============================================================================

API_BASE="https://veritas-engine-zae0.onrender.com"
REPORT_FILE="/tmp/ab_testing_report_$(date +%Y%m%d_%H%M%S).txt"

echo "=============================================="
echo "CEO A/B TESTING SUITE"
echo "Comprehensive Market Readiness Assessment"
echo "$(date)"
echo "=============================================="
echo ""

# Results tracking
declare -A response_times
declare -A status_codes
declare -A test_results

total_tests=0
passed_tests=0
failed_tests=0

# Function to test endpoint and measure response time
test_endpoint_ab() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local expected_status="$5"
    
    echo -n "Testing: $name... "
    
    start_time=$(date +%s%N)
    
    if [ "$method" == "GET" ]; then
        response=$(curl -s -w "\n%{http_code}\n%{time_total}" -o /tmp/response.txt "$API_BASE$endpoint")
    else
        response=$(curl -s -w "\n%{http_code}\n%{time_total}" -X "$method" \
            -H "Content-Type: application/json" \
            -d "$data" \
            -o /tmp/response.txt \
            "$API_BASE$endpoint")
    fi
    
    http_code=$(echo "$response" | sed -n '1p')
    response_time=$(echo "$response" | sed -n '2p')
    response_time_ms=$(echo "$response_time * 1000" | bc)
    
    ((total_tests++))
    
    # Store results
    response_times["$name"]=$response_time_ms
    status_codes["$name"]=$http_code
    
    # Evaluate
    if [ "$http_code" == "$expected_status" ]; then
        echo "✅ PASS (${response_time_ms}ms, HTTP $http_code)"
        ((passed_tests++))
        test_results["$name"]="PASS"
        
        # Check response time thresholds
        if (( $(echo "$response_time_ms > 3000" | bc -l) )); then
            echo "   ⚠️  WARNING: Response time > 3s (degraded UX)"
        elif (( $(echo "$response_time_ms > 1000" | bc -l) )); then
            echo "   ⚡ ACCEPTABLE: Response time 1-3s"
        else
            echo "   🚀 EXCELLENT: Response time < 1s"
        fi
    else
        echo "❌ FAIL (Expected $expected_status, got $http_code)"
        ((failed_tests++))
        test_results["$name"]="FAIL"
        
        # Show error response
        if [ -s /tmp/response.txt ]; then
            echo "   Response: $(head -c 200 /tmp/response.txt)"
        fi
    fi
}

# ==============================================================================
# TEST SUITE 1: CORE INFRASTRUCTURE
# ==============================================================================
echo ""
echo "=== TEST SUITE 1: CORE INFRASTRUCTURE ==="
echo ""

test_endpoint_ab "Health Check" "GET" "/real/health" "" "200"
test_endpoint_ab "Test Status" "GET" "/test/status" "" "200"
test_endpoint_ab "System Check" "GET" "/system/check" "" "200"

# ==============================================================================
# TEST SUITE 2: DOMAIN DISCOVERY (A/B TEST)
# ==============================================================================
echo ""
echo "=== TEST SUITE 2: DOMAIN DISCOVERY (A/B Testing 3 endpoints) ==="
echo ""

test_endpoint_ab "Real Domains" "GET" "/real/domains" "" "200"
test_endpoint_ab "Instant Domains" "GET" "/instant/domains" "" "200"
test_endpoint_ab "Quick Domains" "GET" "/quick/domains" "" "200"

# Compare response times
echo ""
echo "A/B Comparison - Domain Discovery:"
echo "  Real Domains: ${response_times[Real Domains]}ms"
echo "  Instant Domains: ${response_times[Instant Domains]}ms"
echo "  Quick Domains: ${response_times[Quick Domains]}ms"

# ==============================================================================
# TEST SUITE 3: AI ANALYSIS - ALL 10 DOMAINS
# ==============================================================================
echo ""
echo "=== TEST SUITE 3: REAL AI ANALYSIS (All 10 Domains) ==="
echo ""

domains=("legal" "financial" "security" "healthcare" "data-science" "education" "proposals" "ngo" "data-entry" "expenses")

for domain in "${domains[@]}"; do
    data='{"directive":"Analyze for compliance and risks","domain":"'$domain'","document_content":"Sample business document for '$domain' analysis. Contains financial data, contracts, and compliance requirements."}'
    test_endpoint_ab "Real AI - $domain" "POST" "/real/analyze" "$data" "200"
    sleep 1  # Rate limiting
done

# ==============================================================================
# TEST SUITE 4: INSTANT ANALYSIS (A/B vs Real AI)
# ==============================================================================
echo ""
echo "=== TEST SUITE 4: INSTANT ANALYSIS (A/B Test vs Real AI) ==="
echo ""

test_endpoint_ab "Instant Legal" "POST" "/instant/analyze" '{"directive":"Test","domain":"legal"}' "200"
test_endpoint_ab "Instant Financial" "POST" "/instant/analyze" '{"directive":"Test","domain":"financial"}' "200"

# ==============================================================================
# TEST SUITE 5: FUNDING ENGINE
# ==============================================================================
echo ""
echo "=== TEST SUITE 5: FUNDING DOCUMENT SYSTEM ==="
echo ""

test_endpoint_ab "Funding Health" "GET" "/real/funding/health" "" "200"
test_endpoint_ab "Funding Documents List" "GET" "/real/funding/documents" "" "200"

# ==============================================================================
# TEST SUITE 6: EXPENSE MANAGEMENT
# ==============================================================================
echo ""
echo "=== TEST SUITE 6: EXPENSE & RECEIPT SYSTEM ==="
echo ""

test_endpoint_ab "Expense Health" "GET" "/expenses/health" "" "200"
test_endpoint_ab "Expense Summary" "GET" "/expenses/summary?user_id=test&days=30" "" "200"

# ==============================================================================
# GENERATE EXECUTIVE REPORT
# ==============================================================================
echo ""
echo "=============================================="
echo "EXECUTIVE SUMMARY"
echo "=============================================="
echo ""
echo "Total Tests Run: $total_tests"
echo "Passed: $passed_tests ($(echo "scale=1; $passed_tests * 100 / $total_tests" | bc)%)"
echo "Failed: $failed_tests ($(echo "scale=1; $failed_tests * 100 / $total_tests" | bc)%)"
echo ""

# Calculate average response time
total_time=0
count=0
for time in "${response_times[@]}"; do
    total_time=$(echo "$total_time + $time" | bc)
    ((count++))
done
avg_time=$(echo "scale=2; $total_time / $count" | bc)

echo "Performance Metrics:"
echo "  Average Response Time: ${avg_time}ms"
echo ""

# Market Readiness Assessment
if [ $failed_tests -eq 0 ]; then
    if (( $(echo "$avg_time < 1000" | bc -l) )); then
        echo "🏆 MARKET READY: All tests passed, excellent performance"
        exit 0
    elif (( $(echo "$avg_time < 3000" | bc -l) )); then
        echo "✅ MARKET READY: All tests passed, acceptable performance"
        exit 0
    else
        echo "⚠️  CONDITIONAL: All tests passed but performance needs optimization"
        exit 1
    fi
else
    echo "❌ NOT MARKET READY: $failed_tests critical failures detected"
    exit 1
fi
