#!/usr/bin/env python3
"""
CLARITY Engine Test Script
==========================

This script tests the complete CLARITY Engine workflow:
1. Register new user via /auth/register
2. Login via /auth/login
3. Generate API key via dashboard
4. Submit analysis job via /api/analyze/start
5. Poll status via /api/analyze/status/<job_id>
6. Verify JSON result structure

Usage:
    python test_clarity.py [--base-url BASE_URL] [--email EMAIL] [--password PASSWORD]

Example:
    python test_clarity.py --base-url http://localhost:5000 --email test@example.com --password testpass123
"""

import requests
import json
import time
import argparse
import sys
from urllib.parse import urljoin

class ClarityTester:
    def __init__(self, base_url, email, password):
        self.base_url = base_url.rstrip('/')
        self.email = email
        self.password = password
        self.session = requests.Session()
        self.api_key = None
        self.job_id = None
        
    def log(self, message, status="INFO"):
        """Log a message with timestamp and status."""
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{status}] {message}")
    
    def test_register(self):
        """Test user registration."""
        self.log("Testing user registration...")
        
        url = urljoin(self.base_url, '/auth/register')
        data = {
            'email': self.email,
            'password': self.password,
            'password2': self.password,
            'submit': 'Register'
        }
        
        response = self.session.post(url, data=data, allow_redirects=False)
        
        if response.status_code in [200, 302]:
            self.log("✓ User registration successful", "SUCCESS")
            return True
        else:
            self.log(f"✗ User registration failed: {response.status_code}", "ERROR")
            return False
    
    def test_login(self):
        """Test user login."""
        self.log("Testing user login...")
        
        url = urljoin(self.base_url, '/auth/login')
        data = {
            'email': self.email,
            'password': self.password,
            'submit': 'Sign In'
        }
        
        response = self.session.post(url, data=data, allow_redirects=False)
        
        if response.status_code in [200, 302]:
            self.log("✓ User login successful", "SUCCESS")
            return True
        else:
            self.log(f"✗ User login failed: {response.status_code}", "ERROR")
            return False
    
    def test_generate_api_key(self):
        """Test API key generation."""
        self.log("Testing API key generation...")
        
        url = urljoin(self.base_url, '/dashboard/generate-key')
        response = self.session.post(url)
        
        if response.status_code == 201:
            data = response.json()
            self.api_key = data['api_key']
            self.log("✓ API key generated successfully", "SUCCESS")
            self.log(f"API Key: {self.api_key[:20]}...", "INFO")
            return True
        else:
            self.log(f"✗ API key generation failed: {response.status_code}", "ERROR")
            if response.text:
                self.log(f"Response: {response.text}", "ERROR")
            return False
    
    def test_analysis_submission(self):
        """Test analysis job submission."""
        self.log("Testing analysis job submission...")
        
        if not self.api_key:
            self.log("✗ No API key available for analysis test", "ERROR")
            return False
        
        # Create a test document
        test_content = """
        This is a test contract for CLARITY Engine analysis.
        
        CONTRACT TERMS:
        1. The party of the first part agrees to provide services.
        2. Payment shall be made within 30 days of invoice receipt.
        3. This agreement shall be governed by the laws of the State of California.
        4. Either party may terminate this agreement with 30 days written notice.
        
        LIABILITY CLAUSE:
        The maximum liability of either party shall not exceed $100,000.
        """
        
        url = urljoin(self.base_url, '/api/analyze/start')
        headers = {'X-API-KEY': self.api_key}
        
        files = {
            'files': ('test_contract.txt', test_content, 'text/plain')
        }
        data = {
            'directive': 'Analyze this contract for liability risks and compliance issues'
        }
        
        response = self.session.post(url, headers=headers, files=files, data=data)
        
        if response.status_code == 202:
            data = response.json()
            self.job_id = data['job_id']
            self.log("✓ Analysis job submitted successfully", "SUCCESS")
            self.log(f"Job ID: {self.job_id}", "INFO")
            return True
        else:
            self.log(f"✗ Analysis submission failed: {response.status_code}", "ERROR")
            if response.text:
                self.log(f"Response: {response.text}", "ERROR")
            return False
    
    def test_status_polling(self):
        """Test status polling and result retrieval."""
        self.log("Testing status polling...")
        
        if not self.job_id:
            self.log("✗ No job ID available for status test", "ERROR")
            return False
        
        url = urljoin(self.base_url, f'/api/analyze/status/{self.job_id}')
        headers = {'X-API-KEY': self.api_key}
        
        max_attempts = 30  # 30 attempts = 1 minute max
        attempt = 0
        
        while attempt < max_attempts:
            attempt += 1
            self.log(f"Status check attempt {attempt}/{max_attempts}...")
            
            response = self.session.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                state = data.get('state', 'UNKNOWN')
                
                if state == 'SUCCESS':
                    self.log("✓ Analysis completed successfully", "SUCCESS")
                    return self.verify_result_structure(data.get('result', {}))
                elif state == 'FAILURE':
                    self.log(f"✗ Analysis failed: {data.get('error', 'Unknown error')}", "ERROR")
                    return False
                else:
                    self.log(f"Status: {data.get('status', 'Processing...')}")
                    time.sleep(2)
            else:
                self.log(f"✗ Status check failed: {response.status_code}", "ERROR")
                return False
        
        self.log("✗ Analysis timed out after 1 minute", "ERROR")
        return False
    
    def verify_result_structure(self, result):
        """Verify that the result has the expected JSON structure."""
        self.log("Verifying result structure...")
        
        required_fields = [
            'executive_summary',
            'key_findings', 
            'actionable_recommendations',
            'confidence_score',
            'data_gaps'
        ]
        
        missing_fields = []
        for field in required_fields:
            if field not in result:
                missing_fields.append(field)
        
        if missing_fields:
            self.log(f"✗ Result missing required fields: {missing_fields}", "ERROR")
            return False
        
        # Check that key_findings and actionable_recommendations are lists
        if not isinstance(result['key_findings'], list):
            self.log("✗ key_findings should be a list", "ERROR")
            return False
        
        if not isinstance(result['actionable_recommendations'], list):
            self.log("✗ actionable_recommendations should be a list", "ERROR")
            return False
        
        if not isinstance(result['data_gaps'], list):
            self.log("✗ data_gaps should be a list", "ERROR")
            return False
        
        self.log("✓ Result structure verification passed", "SUCCESS")
        self.log(f"Executive Summary: {result['executive_summary'][:100]}...", "INFO")
        self.log(f"Key Findings: {len(result['key_findings'])} items", "INFO")
        self.log(f"Recommendations: {len(result['actionable_recommendations'])} items", "INFO")
        
        return True
    
    def run_full_test(self):
        """Run the complete test suite."""
        self.log("Starting CLARITY Engine full test suite", "INFO")
        self.log("=" * 50, "INFO")
        
        tests = [
            ("User Registration", self.test_register),
            ("User Login", self.test_login),
            ("API Key Generation", self.test_generate_api_key),
            ("Analysis Submission", self.test_analysis_submission),
            ("Status Polling & Results", self.test_status_polling)
        ]
        
        passed = 0
        total = len(tests)
        
        for test_name, test_func in tests:
            self.log(f"\n--- {test_name} ---", "INFO")
            if test_func():
                passed += 1
            else:
                self.log(f"Test '{test_name}' failed. Stopping test suite.", "ERROR")
                break
        
        self.log("\n" + "=" * 50, "INFO")
        self.log(f"Test Results: {passed}/{total} tests passed", "INFO")
        
        if passed == total:
            self.log("🎉 ALL TESTS PASSED! CLARITY Engine is working correctly.", "SUCCESS")
            return True
        else:
            self.log("❌ Some tests failed. Please check the logs above.", "ERROR")
            return False

def main():
    parser = argparse.ArgumentParser(description='Test CLARITY Engine functionality')
    parser.add_argument('--base-url', default='http://localhost:5000',
                       help='Base URL of the CLARITY Engine (default: http://localhost:5000)')
    parser.add_argument('--email', default='test@clarity.ai',
                       help='Test user email (default: test@clarity.ai)')
    parser.add_argument('--password', default='testpass123',
                       help='Test user password (default: testpass123)')
    
    args = parser.parse_args()
    
    tester = ClarityTester(args.base_url, args.email, args.password)
    
    try:
        success = tester.run_full_test()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        tester.log("Test interrupted by user", "WARNING")
        sys.exit(1)
    except Exception as e:
        tester.log(f"Unexpected error: {e}", "ERROR")
        sys.exit(1)

if __name__ == '__main__':
    main()
