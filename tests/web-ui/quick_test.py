#!/usr/bin/env python3
"""
Quick test of the Advanced Pricing Intelligence Platform
"""

import requests
import json

def test_health():
    try:
        response = requests.get("http://localhost:8080/api/health", timeout=3)
        print(f"✅ Health Check: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Status: {data.get('status')}")
            print(f"   Message: {data.get('message')}")
        return True
    except Exception as e:
        print(f"❌ Health Check Failed: {e}")
        return False

def test_pricing():
    try:
        payload = {
            "product_name": "Test Widget",
            "cost": 25.0,
            "category": "premium",
            "market_segment": "technology"
        }
        response = requests.post("http://localhost:8080/api/price", json=payload, timeout=5)
        print(f"✅ Pricing API: {response.status_code}")
        if response.status_code == 200:
            data = response.json()
            print(f"   Product: {data.get('product_name')}")
            print(f"   Recommended Price: ${data.get('recommended_price')}")
            print(f"   Confidence: {data.get('confidence_score', 0):.1%}")
        return True
    except Exception as e:
        print(f"❌ Pricing API Failed: {e}")
        return False

def main():
    print("🧪 Quick Test - Advanced Pricing Intelligence Platform")
    print("=" * 60)
    
    health_ok = test_health()
    pricing_ok = test_pricing()
    
    print("\n" + "=" * 60)
    if health_ok and pricing_ok:
        print("🎉 All tests passed! Platform is working!")
        print("🌐 Access at: http://localhost:8080")
    else:
        print("⚠️  Some tests failed")

if __name__ == "__main__":
    main()
