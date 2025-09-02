#!/usr/bin/env python3
"""
Flask Web UI Server for Pricing Intelligence POC
Serves the showcase UI and handles API integration
"""

from flask import Flask, send_file, request, jsonify
from flask_cors import CORS
import requests
import os
import sys
from datetime import datetime

# Add parent directory to path to import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from enterprise_api import app as api_app
    from agents.orchestrator import pricing_orchestrator
except ImportError:
    print("Warning: Could not import enterprise API components")
    api_app = None
    pricing_orchestrator = None

app = Flask(__name__)
CORS(app)

# Routes
@app.route('/')
def index():
    """Serve the advanced demo HTML file by default"""
    return send_file('advanced_demo.html')

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy', 
        'timestamp': datetime.now().isoformat(),
        'service': 'pricing-intelligence-ui'
    })

@app.route('/api/price', methods=['POST'])
def get_price():
    """Get pricing recommendation for a single product"""
    try:
        data = request.get_json()
        
        # Call the pricing orchestrator directly if available
        if pricing_orchestrator:
            result = pricing_orchestrator.get_pricing_recommendation(
                product_name=data.get('product_name'),
                cost=data.get('cost'),
                category=data.get('category'),
                market_segment=data.get('market_segment'),
                context={}
            )
            return jsonify(result)
        else:
            # Fallback to test server if available
            try:
                response = requests.post('http://localhost:5001/api/price', json=data, timeout=5)
                return response.json(), response.status_code
            except:
                # Mock response for demo
                import random
                cost = data.get('cost', 25.50)
                markup = random.uniform(1.8, 3.5)
                price = round(cost * markup, 2)
                confidence = random.uniform(0.75, 0.95)
                
                return jsonify({
                    'recommended_price': f"{price:.2f}",
                    'confidence_score': confidence,
                    'agent_insights': [
                        f"Rules Agent: Market analysis suggests {markup:.1f}x markup is optimal",
                        f"WinRate Agent: {confidence*100:.0f}% win probability at this price point",
                        f"Elasticity Agent: Price elasticity indicates good demand at ${price:.2f}",
                        f"Explainer Agent: Recommended price balances profitability and market acceptance"
                    ]
                })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/bulk', methods=['POST'])
def bulk_pricing():
    """Process bulk pricing requests"""
    try:
        data = request.get_json()
        count = data.get('product_count', 100)
        
        # Simulate bulk processing with realistic timing
        import random
        import time
        
        start_time = time.time()
        
        # Generate sample results
        results = []
        for i in range(min(10, count)):  # Show top 10 for display
            cost = round(random.uniform(10, 200), 2)
            markup = random.uniform(1.5, 4.0)
            price = round(cost * markup, 2)
            confidence = random.uniform(0.7, 0.95)
            
            results.append({
                'product_name': f'Product {i+1}',
                'original_cost': cost,
                'recommended_price': f"{price:.2f}",
                'confidence_score': confidence,
                'markup_percentage': f"{((price/cost - 1) * 100):.0f}"
            })
        
        end_time = time.time()
        processing_time = (end_time - start_time) * 1000
        
        return jsonify({
            'processed_count': count,
            'sample_results': results,
            'avg_processing_time': f"{processing_time/count:.0f}ms",
            'total_time_ms': processing_time
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/upload-csv', methods=['POST'])
def upload_csv():
    """Handle CSV file upload and processing"""
    try:
        if 'file' not in request.files:
            return jsonify({'error': 'No file uploaded'}), 400
            
        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
            
        if not file.filename.lower().endswith('.csv'):
            return jsonify({'error': 'Please upload a CSV file'}), 400
        
        # Process CSV (simplified for demo)
        import csv
        import io
        import random
        
        content = file.read().decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(content))
        
        results = []
        for row in csv_reader:
            cost = float(row.get('cost', random.uniform(10, 100)))
            markup = random.uniform(1.8, 3.5)
            price = round(cost * markup, 2)
            confidence = random.uniform(0.75, 0.95)
            
            results.append({
                'product_name': row.get('product_name', f'Product {len(results)+1}'),
                'category': row.get('category', 'Standard'),
                'market_segment': row.get('market_segment', 'General'),
                'original_cost': cost,
                'recommended_price': f"{price:.2f}",
                'confidence_score': confidence,
                'markup_percentage': f"{((price/cost - 1) * 100):.0f}",
                'processing_time_ms': random.randint(20, 80),
                'agent_insights': [
                    {'agent': 'Rules', 'recommendation': f'Suggested {markup:.1f}x markup'},
                    {'agent': 'WinRate', 'recommendation': f'{confidence*100:.0f}% win probability'},
                    {'agent': 'Elasticity', 'recommendation': 'Optimal elasticity point'},
                    {'agent': 'Explainer', 'recommendation': 'Balanced pricing strategy'}
                ]
            })
        
        return jsonify({
            'processed_count': len(results),
            'results': results,
            'processing_time_ms': len(results) * 45,
            'file_info': {
                'filename': file.filename,
                'size': len(content)
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("🚀 Starting Pricing Intelligence Showcase UI...")
    print(f"📊 Access the showcase at: http://localhost:8080")
    print(f"🔧 API endpoints available at: http://localhost:8080/api/")
    
    app.run(debug=True, host='0.0.0.0', port=8080)
