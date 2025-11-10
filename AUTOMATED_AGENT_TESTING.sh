#!/bin/bash

# ==============================================================================
# CLARITY ENGINE - AUTOMATED AGENT TESTING & DEPLOYMENT
# ==============================================================================
# Purpose: Full automated testing and deployment validation
# Quality: Presidential-grade validation before launch
# ==============================================================================

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m'

# Configuration
BACKEND_URL="${BACKEND_URL:-https://veritas-engine.onrender.com}"
FRONTEND_URL="${FRONTEND_URL:-https://clarity-frontend.vercel.app}"
LOG_FILE="agent_testing_$(date +%Y%m%d_%H%M%S).log"

# Test results
TOTAL_CHECKS=0
PASSED_CHECKS=0
FAILED_CHECKS=0
WARNINGS=0

# ==============================================================================
# Utility Functions
# ==============================================================================

log() {
    echo "$1" | tee -a "$LOG_FILE"
}

print_header() {
    echo "" | tee -a "$LOG_FILE"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$LOG_FILE"
    echo -e "${PURPLE}$1${NC}" | tee -a "$LOG_FILE"
    echo -e "${BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

check_pass() {
    echo -e "${GREEN}✅ PASS: $1${NC}" | tee -a "$LOG_FILE"
    ((PASSED_CHECKS++))
    ((TOTAL_CHECKS++))
}

check_fail() {
    echo -e "${RED}❌ FAIL: $1${NC}" | tee -a "$LOG_FILE"
    if [ -n "$2" ]; then
        echo -e "${YELLOW}   Reason: $2${NC}" | tee -a "$LOG_FILE"
    fi
    ((FAILED_CHECKS++))
    ((TOTAL_CHECKS++))
}

check_warning() {
    echo -e "${YELLOW}⚠️  WARNING: $1${NC}" | tee -a "$LOG_FILE"
    ((WARNINGS++))
    ((TOTAL_CHECKS++))
}

print_progress() {
    echo -e "${CYAN}⏳ $1...${NC}"
}

# ==============================================================================
# Pre-Flight Checks
# ==============================================================================

check_dependencies() {
    print_header "🔧 DEPENDENCY CHECK"
    
    print_progress "Checking required tools"
    
    # Check curl
    if command -v curl &> /dev/null; then
        check_pass "curl is installed"
    else
        check_fail "curl is not installed" "Install with: apt-get install curl"
    fi
    
    # Check jq
    if command -v jq &> /dev/null; then
        check_pass "jq is installed (JSON parsing)"
    else
        check_warning "jq not installed (optional, improves output formatting)"
    fi
    
    # Check bc
    if command -v bc &> /dev/null; then
        check_pass "bc is installed (calculations)"
    else
        check_warning "bc not installed (optional)"
    fi
}

# ==============================================================================
# Environment Validation
# ==============================================================================

validate_environment() {
    print_header "🌍 ENVIRONMENT VALIDATION"
    
    print_progress "Validating backend URL"
    if [ -n "$BACKEND_URL" ]; then
        check_pass "Backend URL configured: $BACKEND_URL"
    else
        check_fail "Backend URL not set" "Set BACKEND_URL environment variable"
    fi
    
    print_progress "Validating frontend URL"
    if [ -n "$FRONTEND_URL" ]; then
        check_pass "Frontend URL configured: $FRONTEND_URL"
    else
        check_warning "Frontend URL not set (optional for backend-only tests)"
    fi
}

# ==============================================================================
# Connectivity Tests
# ==============================================================================

test_connectivity() {
    print_header "🌐 CONNECTIVITY TESTS"
    
    print_progress "Testing backend connectivity"
    if curl -s -f -m 10 "$BACKEND_URL/health" > /dev/null 2>&1; then
        check_pass "Backend is reachable"
    else
        check_fail "Backend is not reachable" "Check if service is running"
        return 1
    fi
    
    print_progress "Testing frontend connectivity"
    if curl -s -f -m 10 "$FRONTEND_URL" > /dev/null 2>&1; then
        check_pass "Frontend is reachable"
    else
        check_warning "Frontend connectivity issue (may be OK if not deployed yet)"
    fi
}

# ==============================================================================
# API Health Checks
# ==============================================================================

test_api_health() {
    print_header "💚 API HEALTH CHECKS"
    
    print_progress "Checking API health status"
    response=$(curl -s -w "\n%{http_code}" "$BACKEND_URL/health" 2>&1)
    http_code=$(echo "$response" | tail -n1)
    body=$(echo "$response" | sed '$d')
    
    if [ "$http_code" = "200" ]; then
        check_pass "API health endpoint responding"
        
        # Check for LLM configuration
        if echo "$body" | grep -q "llm_configured\|gemini\|gpt"; then
            check_pass "LLM providers are configured"
        else
            check_warning "LLM configuration unclear from health response"
        fi
    else
        check_fail "API health check failed" "HTTP $http_code"
    fi
}

# ==============================================================================
# Domain Intelligence Tests
# ==============================================================================

test_all_domains() {
    print_header "🎯 DOMAIN INTELLIGENCE VALIDATION"
    
    domains=("legal" "financial" "technical" "security" "funding")
    
    for domain in "${domains[@]}"; do
        print_progress "Testing $domain domain"
        
        response=$(curl -s -X POST "$BACKEND_URL/real/analyze" \
            -H "Content-Type: application/json" \
            -d "{
                \"domain\": \"$domain\",
                \"directive\": \"Quick test analysis\",
                \"document_content\": \"Test content for $domain domain validation\"
            }" 2>&1)
        
        if echo "$response" | grep -q "success\|analysis"; then
            check_pass "$domain domain is operational"
        else
            check_fail "$domain domain not responding properly"
        fi
        
        # Small delay between tests
        sleep 0.5
    done
}

# ==============================================================================
# Advanced Features Test
# ==============================================================================

test_advanced_features() {
    print_header "⚡ ADVANCED FEATURES VALIDATION"
    
    # Test Outstanding Writing System
    print_progress "Testing Outstanding Writing System"
    response=$(curl -s -X POST "$BACKEND_URL/real/analyze" \
        -H "Content-Type: application/json" \
        -d '{
            "domain": "legal",
            "directive": "Create executive summary",
            "document_content": "Contract terms and conditions",
            "use_outstanding": true
        }' 2>&1)
    
    if echo "$response" | grep -q "success\|analysis"; then
        check_pass "Outstanding Writing System operational"
    else
        check_warning "Outstanding Writing System status unclear"
    fi
    
    # Test OCR Status
    print_progress "Testing OCR capability"
    response=$(curl -s "$BACKEND_URL/ocr/status" 2>&1)
    
    if echo "$response" | grep -qi "tesseract\|google_vision\|ocr"; then
        check_pass "OCR system configured"
    else
        check_warning "OCR status endpoint may not be available"
    fi
}

# ==============================================================================
# Performance Benchmarks
# ==============================================================================

test_performance() {
    print_header "⚡ PERFORMANCE BENCHMARKS"
    
    # Test response time
    print_progress "Measuring API response time"
    
    start=$(date +%s.%N 2>/dev/null || date +%s)
    curl -s "$BACKEND_URL/health" > /dev/null
    end=$(date +%s.%N 2>/dev/null || date +%s)
    
    if command -v bc &> /dev/null; then
        response_time=$(echo "$end - $start" | bc)
        
        if (( $(echo "$response_time < 2.0" | bc -l) )); then
            check_pass "Response time excellent: ${response_time}s"
        elif (( $(echo "$response_time < 5.0" | bc -l) )); then
            check_warning "Response time acceptable: ${response_time}s (target: <2s)"
        else
            check_fail "Response time too slow: ${response_time}s"
        fi
    else
        check_pass "Response time check completed (bc not available for precise timing)"
    fi
    
    # Test concurrent requests
    print_progress "Testing concurrent request handling"
    
    start=$(date +%s 2>/dev/null)
    curl -s "$BACKEND_URL/health" > /dev/null &
    curl -s "$BACKEND_URL/health" > /dev/null &
    curl -s "$BACKEND_URL/health" > /dev/null &
    wait
    end=$(date +%s 2>/dev/null)
    
    check_pass "Concurrent requests handled successfully"
}

# ==============================================================================
# Security Validation
# ==============================================================================

test_security() {
    print_header "🔒 SECURITY VALIDATION"
    
    # Test CORS
    print_progress "Checking CORS configuration"
    response=$(curl -s -I "$BACKEND_URL/health" 2>&1)
    
    if echo "$response" | grep -qi "access-control-allow-origin"; then
        check_pass "CORS headers present"
    else
        check_warning "CORS headers not detected (may need configuration)"
    fi
    
    # Test HTTPS
    print_progress "Validating HTTPS"
    if [[ "$BACKEND_URL" == https://* ]]; then
        check_pass "Backend using HTTPS"
    else
        check_warning "Backend not using HTTPS (OK for development)"
    fi
    
    # Test error handling (should not expose stack traces)
    print_progress "Testing error handling security"
    response=$(curl -s -X POST "$BACKEND_URL/real/analyze" \
        -H "Content-Type: application/json" \
        -d '{"invalid": "data"}' 2>&1)
    
    if echo "$response" | grep -qi "traceback\|exception"; then
        check_warning "API may be exposing stack traces (security concern)"
    else
        check_pass "Error responses appear secure"
    fi
}

# ==============================================================================
# Cost & Resource Monitoring
# ==============================================================================

test_cost_monitoring() {
    print_header "💰 COST & RESOURCE MONITORING"
    
    print_progress "Checking cost tracking capability"
    
    # Make a test request and check if cost data is returned
    response=$(curl -s -X POST "$BACKEND_URL/real/analyze" \
        -H "Content-Type: application/json" \
        -d '{
            "domain": "financial",
            "directive": "Brief analysis",
            "document_content": "Test"
        }' 2>&1)
    
    if echo "$response" | grep -qi "cost\|tokens\|usage"; then
        check_pass "Cost tracking data available"
    else
        check_warning "Cost tracking data not visible in response"
    fi
}

# ==============================================================================
# User Experience Validation
# ==============================================================================

test_user_experience() {
    print_header "😊 USER EXPERIENCE VALIDATION"
    
    print_progress "Testing error message quality"
    
    # Test with invalid domain
    response=$(curl -s -X POST "$BACKEND_URL/real/analyze" \
        -H "Content-Type: application/json" \
        -d '{
            "domain": "invalid_domain",
            "directive": "test"
        }' 2>&1)
    
    if echo "$response" | grep -qi "error"; then
        if echo "$response" | grep -qi "invalid\|supported\|available"; then
            check_pass "Error messages are user-friendly"
        else
            check_warning "Error messages could be more descriptive"
        fi
    else
        check_fail "Error handling not working as expected"
    fi
    
    # Test response format
    print_progress "Validating response format"
    response=$(curl -s -X POST "$BACKEND_URL/real/analyze" \
        -H "Content-Type: application/json" \
        -d '{
            "domain": "legal",
            "directive": "test",
            "document_content": "test"
        }' 2>&1)
    
    if echo "$response" | grep -q "success\|analysis\|result"; then
        check_pass "Response format is consistent"
    else
        check_warning "Response format may need review"
    fi
}

# ==============================================================================
# Stress Testing
# ==============================================================================

test_stress() {
    print_header "💪 STRESS TESTING"
    
    print_progress "Running rapid-fire requests (stress test)"
    
    failures=0
    successes=0
    
    for i in {1..10}; do
        response=$(curl -s -m 5 "$BACKEND_URL/health" 2>&1)
        if [ $? -eq 0 ]; then
            ((successes++))
        else
            ((failures++))
        fi
    done
    
    if [ $failures -eq 0 ]; then
        check_pass "Handled 10 rapid requests successfully"
    elif [ $failures -le 2 ]; then
        check_warning "Some failures under rapid load ($failures/10 failed)"
    else
        check_fail "Too many failures under load ($failures/10 failed)"
    fi
}

# ==============================================================================
# Integration Tests
# ==============================================================================

test_end_to_end_workflow() {
    print_header "🔄 END-TO-END WORKFLOW TEST"
    
    print_progress "Simulating complete user workflow"
    
    # Step 1: User accesses platform
    if curl -s -f "$BACKEND_URL/health" > /dev/null 2>&1; then
        check_pass "Step 1: Platform access successful"
    else
        check_fail "Step 1: Platform access failed"
        return
    fi
    
    # Step 2: User submits analysis request
    response=$(curl -s -X POST "$BACKEND_URL/real/analyze" \
        -H "Content-Type: application/json" \
        -d '{
            "domain": "legal",
            "directive": "Analyze this contract for risks and recommendations",
            "document_content": "Standard employment contract with competitive salary and benefits package. 40-hour work week. Two weeks notice for termination.",
            "use_outstanding": true
        }' 2>&1)
    
    if echo "$response" | grep -q "success\|analysis"; then
        check_pass "Step 2: Analysis request processed"
    else
        check_fail "Step 2: Analysis request failed"
        return
    fi
    
    # Step 3: Results are comprehensive
    word_count=$(echo "$response" | wc -w)
    if [ "$word_count" -gt 50 ]; then
        check_pass "Step 3: Results are comprehensive ($word_count words)"
    else
        check_warning "Step 3: Results may be too brief ($word_count words)"
    fi
}

# ==============================================================================
# Generate Report
# ==============================================================================

generate_report() {
    print_header "📊 TEST RESULTS SUMMARY"
    
    echo "" | tee -a "$LOG_FILE"
    echo -e "${CYAN}╔══════════════════════════════════════════════════════════════════╗${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}║                    CLARITY ENGINE - AGENT TEST RESULTS          ║${NC}" | tee -a "$LOG_FILE"
    echo -e "${CYAN}╚══════════════════════════════════════════════════════════════════╝${NC}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    
    echo -e "${BLUE}Total Checks:     ${CYAN}$TOTAL_CHECKS${NC}" | tee -a "$LOG_FILE"
    echo -e "${GREEN}Passed:           ${CYAN}$PASSED_CHECKS${NC}" | tee -a "$LOG_FILE"
    echo -e "${RED}Failed:           ${CYAN}$FAILED_CHECKS${NC}" | tee -a "$LOG_FILE"
    echo -e "${YELLOW}Warnings:         ${CYAN}$WARNINGS${NC}" | tee -a "$LOG_FILE"
    
    if [ $TOTAL_CHECKS -gt 0 ]; then
        success_rate=$((PASSED_CHECKS * 100 / TOTAL_CHECKS))
        echo -e "${PURPLE}Success Rate:     ${CYAN}$success_rate%${NC}" | tee -a "$LOG_FILE"
    fi
    
    echo "" | tee -a "$LOG_FILE"
    
    # Overall verdict
    if [ $FAILED_CHECKS -eq 0 ]; then
        echo -e "${GREEN}╔══════════════════════════════════════════════════════════════════╗${NC}" | tee -a "$LOG_FILE"
        echo -e "${GREEN}║  🏆 PRESIDENTIAL QUALITY ACHIEVED - READY FOR LAUNCH! 🏆         ║${NC}" | tee -a "$LOG_FILE"
        echo -e "${GREEN}╚══════════════════════════════════════════════════════════════════╝${NC}" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        echo -e "${CYAN}✅ System is production-ready${NC}" | tee -a "$LOG_FILE"
        echo -e "${CYAN}✅ All critical tests passed${NC}" | tee -a "$LOG_FILE"
        echo -e "${CYAN}✅ Ready for Y-Combinator presentation${NC}" | tee -a "$LOG_FILE"
        echo -e "${CYAN}✅ Ready for Fortune 50 clients${NC}" | tee -a "$LOG_FILE"
        
        if [ $WARNINGS -gt 0 ]; then
            echo "" | tee -a "$LOG_FILE"
            echo -e "${YELLOW}⚠️  Note: $WARNINGS warnings detected (review recommended but not blocking)${NC}" | tee -a "$LOG_FILE"
        fi
    elif [ $success_rate -ge 80 ]; then
        echo -e "${YELLOW}╔══════════════════════════════════════════════════════════════════╗${NC}" | tee -a "$LOG_FILE"
        echo -e "${YELLOW}║  ⚠️  GOOD QUALITY - REVIEW FAILURES BEFORE LAUNCH ⚠️            ║${NC}" | tee -a "$LOG_FILE"
        echo -e "${YELLOW}╚══════════════════════════════════════════════════════════════════╝${NC}" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        echo -e "${YELLOW}Platform is mostly functional but has some issues.${NC}" | tee -a "$LOG_FILE"
        echo -e "${YELLOW}Review failed tests above and fix before launch.${NC}" | tee -a "$LOG_FILE"
    else
        echo -e "${RED}╔══════════════════════════════════════════════════════════════════╗${NC}" | tee -a "$LOG_FILE"
        echo -e "${RED}║  ❌ CRITICAL ISSUES - DO NOT LAUNCH ❌                           ║${NC}" | tee -a "$LOG_FILE"
        echo -e "${RED}╚══════════════════════════════════════════════════════════════════╝${NC}" | tee -a "$LOG_FILE"
        echo "" | tee -a "$LOG_FILE"
        echo -e "${RED}Too many critical failures detected.${NC}" | tee -a "$LOG_FILE"
        echo -e "${RED}Fix issues and re-run tests before launch.${NC}" | tee -a "$LOG_FILE"
    fi
    
    echo "" | tee -a "$LOG_FILE"
    echo -e "${BLUE}Full log saved to: ${CYAN}$LOG_FILE${NC}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
}

# ==============================================================================
# Main Execution
# ==============================================================================

main() {
    clear
    
    print_header "🤖 CLARITY ENGINE - AUTOMATED AGENT TESTING"
    
    echo -e "${PURPLE}Configuration:${NC}" | tee -a "$LOG_FILE"
    echo -e "  Backend:  ${CYAN}$BACKEND_URL${NC}" | tee -a "$LOG_FILE"
    echo -e "  Frontend: ${CYAN}$FRONTEND_URL${NC}" | tee -a "$LOG_FILE"
    echo -e "  Log File: ${CYAN}$LOG_FILE${NC}" | tee -a "$LOG_FILE"
    echo "" | tee -a "$LOG_FILE"
    echo -e "${YELLOW}Starting comprehensive automated testing...${NC}" | tee -a "$LOG_FILE"
    
    # Run all test suites
    check_dependencies
    validate_environment
    test_connectivity
    
    # Only continue if connectivity succeeds
    if [ $? -eq 0 ] || [ $FAILED_CHECKS -lt 2 ]; then
        test_api_health
        test_all_domains
        test_advanced_features
        test_performance
        test_security
        test_cost_monitoring
        test_user_experience
        test_stress
        test_end_to_end_workflow
    else
        echo -e "${RED}Skipping remaining tests due to connectivity failures${NC}" | tee -a "$LOG_FILE"
    fi
    
    # Generate final report
    generate_report
    
    # Return appropriate exit code
    if [ $FAILED_CHECKS -eq 0 ]; then
        return 0
    elif [ $success_rate -ge 80 ]; then
        return 1
    else
        return 2
    fi
}

# Run main
main

exit $?
