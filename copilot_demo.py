#!/usr/bin/env python3
"""
Microsoft 365 Copilot Integration Demo
Simulates how users interact with the pricing system through natural language
"""

import json
import random

def simulate_copilot_interaction():
    """Simulate Microsoft 365 Copilot interactions with pricing intelligence"""
    
    print("🤖 Microsoft 365 Copilot - Pricing Intelligence Demo")
    print("=" * 60)
    print()
    
    # Scenario 1: Sales Rep in Outlook
    print("📧 Scenario 1: Sales Rep in Outlook")
    print("-" * 40)
    user_query = "Copilot, what should I price SKU WIDGET-001 for Contoso Corp with 500 units?"
    print(f"👤 User: \"{user_query}\"")
    print()
    
    # Simulate Copilot calling GetPriceRecommendation
    recommendation = {
        "recommended_price": 87.50,
        "win_probability": 78.2,
        "expected_margin": 23.4,
        "confidence": 85.6,
        "volume_tier": "large",
        "discount_applied": 12.0
    }
    
    print("🤖 Copilot: Based on your Pricing Intelligence system:")
    print(f"   💰 Recommended Price: ${recommendation['recommended_price']:.2f} per unit")
    print(f"   🎯 Win Probability: {recommendation['win_probability']:.1f}%")
    print(f"   📊 Expected Margin: {recommendation['expected_margin']:.1f}%")
    print(f"   🏷️  Volume Discount: {recommendation['discount_applied']:.1f}%")
    print("   📝 Strategic Notes: Enterprise customer qualifies for volume discount")
    print()
    
    # Scenario 2: Sales Manager in Teams
    print("👥 Scenario 2: Sales Manager in Teams")
    print("-" * 40)
    user_query = "How competitive is our $95 price point for this deal?"
    print(f"👤 User: \"{user_query}\"")
    print()
    
    # Simulate Copilot calling ScorePrice
    score_result = {
        "price_score": 65.0,
        "win_probability": 65.4,
        "market_position": "+8%",
        "competitive_range": {"min": 88, "max": 92}
    }
    
    print("🤖 Copilot: Your pricing analysis shows:")
    print(f"   🎯 Win Probability: {score_result['win_probability']:.1f}% at $95")
    print(f"   📈 Market Position: {score_result['market_position']} above competitor average")
    print(f"   💡 Recommendation: Consider ${score_result['competitive_range']['min']}-${score_result['competitive_range']['max']} range for 75-85% win rate")
    print()
    
    # Scenario 3: Executive in PowerPoint
    print("📊 Scenario 3: Executive in PowerPoint")
    print("-" * 40)
    user_query = "Add pricing analysis for our Q4 product launch"
    print(f"👤 User: \"{user_query}\"")
    print()
    
    # Simulate Copilot calling GetWinCurve
    win_curve_data = [
        {"price": 80, "win_rate": 92},
        {"price": 85, "win_rate": 85},
        {"price": 90, "win_rate": 76},
        {"price": 95, "win_rate": 65},
        {"price": 100, "win_rate": 52}
    ]
    
    print("🤖 Copilot: I've inserted a pricing analysis chart showing:")
    print("   📈 Price Elasticity Curves:")
    for point in win_curve_data:
        print(f"      ${point['price']}: {point['win_rate']}% win rate")
    print("   🎯 Competitive Positioning: Optimal range $85-$90")
    print("   💰 Expected Revenue Scenarios: $85 = high volume, $90 = balanced")
    print("   📊 Win Rate Projections: 65-85% based on pricing strategy")
    print()
    
    # Scenario 4: Quick Query in Any App
    print("⚡ Scenario 4: Quick Query in Any Microsoft 365 App")
    print("-" * 40)
    user_query = "What's the floor price for SKU ABC-123?"
    print(f"👤 User: \"{user_query}\"")
    print()
    
    floor_price = {
        "floor_price": 72.00,
        "target_price": 85.00,
        "stretch_price": 98.00,
        "cost_basis": 60.00
    }
    
    print("🤖 Copilot: Pricing boundaries for SKU ABC-123:")
    print(f"   🔻 Floor Price: ${floor_price['floor_price']:.2f} (20% margin)")
    print(f"   🎯 Target Price: ${floor_price['target_price']:.2f} (30% margin)")
    print(f"   🚀 Stretch Price: ${floor_price['stretch_price']:.2f} (40% margin)")
    print(f"   ⚠️  Cost Basis: ${floor_price['cost_basis']:.2f} (do not go below)")
    print()

def demonstrate_api_calls():
    """Show the actual API calls made by Copilot"""
    
    print("🔧 Behind the Scenes: API Calls")
    print("=" * 60)
    
    # Example 1: GetPriceRecommendation
    print("1️⃣ GetPriceRecommendation API Call:")
    api_request = {
        "operationId": "getPriceRecommendation",
        "requestBody": {
            "sku": "WIDGET-001",
            "customer_id": "CONTOSO-CORP",
            "quantity": 500,
            "country": "US",
            "channel": "direct",
            "currency": "USD"
        }
    }
    
    api_response = {
        "recommended_price": 87.50,
        "win_probability": 78.2,
        "confidence": 85.6,
        "explanation": "Enterprise customer with large volume qualifies for tier 3 pricing"
    }
    
    print("   📤 Request:", json.dumps(api_request, indent=6))
    print("   📥 Response:", json.dumps(api_response, indent=6))
    print()
    
    # Example 2: ScorePrice
    print("2️⃣ ScorePrice API Call:")
    score_request = {
        "operationId": "scorePrice",
        "requestBody": {
            "sku": "WIDGET-002",
            "proposed_price": 95.00,
            "customer_id": "ACME-CORP",
            "quantity": 200
        }
    }
    
    score_response = {
        "score": 65.4,
        "win_probability": 65.4,
        "market_comparison": "8% above average",
        "recommendations": ["Consider $88-$92 range for better win rate"]
    }
    
    print("   📤 Request:", json.dumps(score_request, indent=6))
    print("   📥 Response:", json.dumps(score_response, indent=6))
    print()

def show_deployment_checklist():
    """Show what's needed to deploy the Copilot integration"""
    
    print("✅ Deployment Checklist for Microsoft 365 Copilot")
    print("=" * 60)
    
    checklist = [
        ("Azure AD App Registration", "✅", "Register app with api://pricing-poc identifier"),
        ("OAuth2 Configuration", "✅", "Authorization and token URLs configured"),
        ("Plugin Manifest", "✅", "manifest.json with 4 actions defined"),
        ("API Reference", "✅", "OpenAPI specification linked"),
        ("Permissions Configuration", "⏳", "Configure scopes: api://pricing-poc/user_impersonation"),
        ("Upload to Microsoft 365", "⏳", "Upload manifest to Teams admin center"),
        ("User Testing", "⏳", "Test with pilot user group"),
        ("Organization Deployment", "⏳", "Deploy to sales teams"),
    ]
    
    for item, status, description in checklist:
        print(f"{status} {item}")
        print(f"    {description}")
    
    print()
    print("🎯 Next Steps:")
    print("   1. Complete Azure AD app registration")
    print("   2. Upload plugin to Microsoft 365 admin center")
    print("   3. Test with pilot sales team")
    print("   4. Deploy organization-wide")
    print("   5. Train users on natural language queries")

def main():
    """Run the complete Microsoft 365 Copilot demo"""
    
    simulate_copilot_interaction()
    print()
    demonstrate_api_calls()
    print()
    show_deployment_checklist()
    
    print()
    print("🎉 Microsoft 365 Copilot Integration Summary:")
    print("   🗣️  Natural language pricing queries")
    print("   📱 Works across all Microsoft 365 apps")
    print("   🔒 Secure OAuth2 authentication")
    print("   🤖 4 AI-powered pricing actions")
    print("   ⚡ Real-time multi-agent processing")
    print("   📊 Contextual business intelligence")

if __name__ == "__main__":
    main()
