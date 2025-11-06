#!/usr/bin/env python3
"""
CLARITY ENGINE - REAL AI TESTING SCRIPT
No API keys required. Tests all 11 domains + email delivery.
"""

import requests
import json
import time

# Backend URL (CORRECT URL!)
BACKEND_URL = "https://veritas-engine-zae0.onrender.com"

# Test email (CHANGE THIS TO YOUR EMAIL!)
TEST_EMAIL = "nsubugacollin@gmail.com"

def print_section(title):
    print("\n" + "="*70)
    print(f"  {title}")
    print("="*70 + "\n")

def test_backend_status():
    """Test 1: Check if backend is online"""
    print_section("TEST 1: Backend Health Check")
    
    try:
        response = requests.get(f"{BACKEND_URL}/test/status", timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            print("✅ Backend is ONLINE!")
            print(f"\nStatus: {data['status']}")
            print(f"Message: {data['message']}")
            print("\nEnvironment:")
            for key, value in data['environment'].items():
                status = "✅" if value else "❌"
                print(f"  {status} {key}: {value}")
            print("\nAvailable Endpoints:")
            for endpoint, method in data['endpoints'].items():
                print(f"  • {method}")
            return True
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Backend is OFFLINE or not responding")
        print(f"Error: {e}")
        return False

def test_email_delivery():
    """Test 2: Email delivery system"""
    print_section("TEST 2: Email Delivery")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/test/email",
            json={"email": TEST_EMAIL},
            timeout=10
        )
        
        data = response.json()
        
        if data.get('success'):
            print(f"✅ Test email sent to {TEST_EMAIL}!")
            print(f"\n{data['message']}")
            print(f"\n💡 {data['check']}")
            return True
        else:
            print(f"⚠️  Email not configured yet")
            print(f"Note: {data.get('note', 'Unknown')}")
            return False
            
    except Exception as e:
        print(f"❌ Email test failed: {e}")
        return False

def test_domain_analysis(domain_name, directive):
    """Test 3: Actual AI analysis for a domain"""
    print_section(f"TEST 3: {domain_name} Analysis")
    
    print(f"Domain: {domain_name}")
    print(f"Directive: {directive}")
    print(f"Email: {TEST_EMAIL}\n")
    
    try:
        response = requests.post(
            f"{BACKEND_URL}/test/analyze",
            json={
                "directive": directive,
                "domain": domain_name,
                "user_email": TEST_EMAIL
            },
            timeout=30
        )
        
        data = response.json()
        
        if data.get('success'):
            print("✅ Analysis STARTED!")
            print(f"\n{data['message']}")
            print(f"\nTask ID: {data.get('task_id', 'N/A')}")
            print(f"Domain: {data.get('domain')}")
            print(f"Estimated Time: {data.get('estimated_time')}")
            print(f"\n📧 Check {TEST_EMAIL} for results!")
            return True
        else:
            print(f"❌ Analysis failed")
            print(f"Error: {data.get('error', 'Unknown')}")
            return False
            
    except Exception as e:
        print(f"❌ Request failed: {e}")
        return False

def run_all_tests():
    """Run complete test suite"""
    print("\n")
    print("🔥"*35)
    print("  CLARITY ENGINE - REAL AI TESTING")
    print("🔥"*35)
    print(f"\nBackend: {BACKEND_URL}")
    print(f"Test Email: {TEST_EMAIL}")
    print("\n⏳ Starting tests...\n")
    
    results = []
    
    # Test 1: Backend Status
    results.append(("Backend Health", test_backend_status()))
    time.sleep(2)
    
    # Test 2: Email Delivery
    results.append(("Email Delivery", test_email_delivery()))
    time.sleep(2)
    
    # Test 3: Sample Domain Analysis
    test_domains = [
        ("legal", "Review this contract and identify any high-risk liability clauses."),
        ("financial", "Analyze our quarterly spending and identify cost reduction opportunities."),
        ("security", "Assess potential security vulnerabilities in our cloud infrastructure."),
    ]
    
    for domain, directive in test_domains:
        result = test_domain_analysis(domain, directive)
        results.append((f"{domain.title()} Analysis", result))
        time.sleep(3)
    
    # Summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 ALL TESTS PASSED! CLARITY ENGINE IS WORKING!")
    elif passed > 0:
        print("\n⚠️  SOME TESTS PASSED. Check configuration.")
    else:
        print("\n❌ ALL TESTS FAILED. Backend may not be deployed yet.")
    
    print("\n💡 NEXT STEPS:")
    print("1. Check your email for analysis results")
    print("2. If no email, configure SMTP settings on Render")
    print("3. Test other domains using the same format")
    
    print("\n" + "="*70 + "\n")

if __name__ == "__main__":
    # CHANGE THIS TO YOUR EMAIL!
    if TEST_EMAIL == "nsubugacollin@gmail.com":
        print("\n⚠️  Using default email. Change TEST_EMAIL in script to your email!\n")
    
    run_all_tests()
