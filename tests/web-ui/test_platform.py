#!/usr/bin/env python3
"""
Comprehensive test suite for the Advanced Pricing Intelligence Platform
"""

import requests
import json
import time
import sys
from datetime import datetime

def print_test_header(test_name):
    print(f"\n{'='*60}")
    print(f"🧪 {test_name}")
    print(f"{'='*60}")

def print_result(test_name, success, message="", data=None):
    status = "✅ PASS" if success else "❌ FAIL"
    print(f"{status} {test_name}")
    if message:
        print(f"   {message}")
    if data:
        print(f"   Response: {json.dumps(data, indent=2)}")

def test_api_health():
    """Test API health endpoint"""
    try:
        response = requests.get("http://localhost:8080/api/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            return True, "API is healthy", data
        else:
            return False, f"HTTP {response.status_code}", None
    except Exception as e:
        return False, str(e), None

def test_single_pricing():
    """Test single product pricing"""
    try:
        payload = {
            "product_name": "Premium Test Widget",
            "cost": 45.75,
            "category": "premium",
            "market_segment": "technology"
        }
        
        response = requests.post(
            "http://localhost:8080/api/price",
            json=payload,
            timeout=10
        )
        
        if response.status_code == 200:
            data = response.json()
            if "recommended_price" in data and "confidence_score" in data:
                return True, f"Price: ${data['recommended_price']}, Confidence: {data['confidence_score']:.1%}", data
            else:
                return False, "Missing required fields in response", data
        else:
            return False, f"HTTP {response.status_code}", None
    except Exception as e:
        return False, str(e), None

def test_bulk_pricing():
    """Test bulk pricing functionality"""
    try:
        products = [
            {"product_name": f"Product {i}", "cost": 20 + i, "category": "standard", "market_segment": "retail"}
            for i in range(1, 6)
        ]
        
        payload = {"products": products}
        
        response = requests.post(
            "http://localhost:8080/api/bulk",
            json=payload,
            timeout=15
        )
        
        if response.status_code == 200:
            data = response.json()
            if "processed_count" in data and data["processed_count"] == 5:
                return True, f"Processed {data['processed_count']} products in {data['processing_time_ms']}ms", data
            else:
                return False, "Incorrect processing count", data
        else:
            return False, f"HTTP {response.status_code}", None
    except Exception as e:
        return False, str(e), None

def test_ui_availability():
    """Test UI availability"""
    try:
        response = requests.get("http://localhost:8080/", timeout=5)
        if response.status_code == 200:
            content = response.text
            if "Advanced Pricing Intelligence" in content and "html" in content.lower():
                return True, "UI loads successfully", {"content_length": len(content)}
            else:
                return False, "UI content invalid", None
        else:
            return False, f"HTTP {response.status_code}", None
    except Exception as e:
        return False, str(e), None

def main():
    print("🚀 Advanced Pricing Intelligence Platform - Test Suite")
    print(f"📅 Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    tests = [
        ("API Health Check", test_api_health),
        ("UI Availability", test_ui_availability),
        ("Single Product Pricing", test_single_pricing),
        ("Bulk Pricing (5 products)", test_bulk_pricing),
    ]
    
    results = []
    
    for test_name, test_func in tests:
        print_test_header(test_name)
        try:
            success, message, data = test_func()
            print_result(test_name, success, message, data)
            results.append((test_name, success))
        except Exception as e:
            print_result(test_name, False, f"Test error: {str(e)}")
            results.append((test_name, False))
        
        time.sleep(0.5)  # Brief pause between tests
    
    # Summary
    print_test_header("Test Summary")
    passed = sum(1 for _, success in results if success)
    total = len(results)
    
    print(f"📊 Results: {passed}/{total} tests passed")
    
    for test_name, success in results:
        status = "✅" if success else "❌"
        print(f"   {status} {test_name}")
    
    if passed == total:
        print(f"\n🎉 All tests passed! The Advanced Pricing Intelligence Platform is working perfectly!")
        print(f"🌐 Access the platform at: http://localhost:8080")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed. Please check the server status.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
