#!/usr/bin/env python3
"""
Simple test server for the advanced demo
"""

from flask import Flask, send_file, request, jsonify
from flask_cors import CORS
import random
import time

app = Flask(__name__)
CORS(app)

@app.route('/')
def index():
    """Serve the advanced demo"""
    return send_file('advanced_demo.html')

@app.route('/simple')
def simple_demo():
    """Serve the simple demo"""
    return send_file('simple_demo.html')

@app.route('/api/health')
def health_check():
    """API health check"""
    return jsonify({
        "status": "healthy",
        "message": "Pricing Intelligence API is running",
        "timestamp": time.time(),
        "version": "1.0.0"
    })

@app.route('/api/price', methods=['POST'])
def predict_price():
    """Single product pricing endpoint"""
    data = request.get_json()
    
    # Simulate pricing calculation
    base_price = data.get('cost', 0) * random.uniform(1.5, 3.0)
    
    # Simulate agent responses
    result = {
        "product_name": data.get('product_name', 'Unknown Product'),
        "recommended_price": round(base_price, 2),
        "confidence_score": random.uniform(0.75, 0.95),
        "agent_results": {
            "rules_agent": {"price": round(base_price * 0.9, 2), "reasoning": "Applied category rules"},
            "winrate_agent": {"price": round(base_price * 1.1, 2), "reasoning": "Market competitiveness"},
            "elasticity_agent": {"price": round(base_price, 2), "reasoning": "Demand elasticity analysis"},
            "explainer_agent": {"explanation": "Price optimized for market conditions"}
        }
    }
    
    # Simulate processing delay
    time.sleep(0.5)
    
    return jsonify(result)

@app.route('/api/bulk', methods=['POST'])
def bulk_pricing():
    """Bulk pricing endpoint"""
    data = request.get_json()
    products = data.get('products', [])
    
    start_time = time.time()
    results = []
    
    for product in products:
        base_price = product.get('cost', 0) * random.uniform(1.5, 3.0)
        results.append({
            "product_name": product.get('product_name', 'Unknown'),
            "recommended_price": round(base_price, 2),
            "confidence_score": random.uniform(0.75, 0.95),
            "category": product.get('category', 'unknown'),
            "market_segment": product.get('market_segment', 'unknown')
        })
    
    processing_time = int((time.time() - start_time) * 1000)
    
    return jsonify({
        "processed_count": len(results),
        "results": results,
        "processing_time_ms": processing_time,
        "status": "completed"
    })

@app.route('/api/upload-csv', methods=['POST'])
def upload_csv():
    """CSV upload endpoint"""
    # Simulate CSV processing
    time.sleep(1)
    
    # Return mock results
    return jsonify({
        "processed_count": 50,
        "results": [
            {
                "product_name": f"Product {i}",
                "recommended_price": round(random.uniform(10, 200), 2),
                "confidence_score": random.uniform(0.75, 0.95)
            } for i in range(50)
        ],
        "processing_time_ms": 1000,
        "status": "completed"
    })

if __name__ == '__main__':
    print("🚀 Starting Advanced Pricing Intelligence Demo...")
    print("📊 Access at: http://localhost:8080")
    print("🔧 API endpoints: /api/health, /api/price, /api/bulk, /api/upload-csv")
    app.run(host='0.0.0.0', port=8080, debug=True)
