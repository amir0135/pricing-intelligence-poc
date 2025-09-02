"""
Simple FastAPI server for the multi-agent pricing intelligence system.
This demonstrates the API without requiring complex ML dependencies.
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import uvicorn
import sys
import os

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

# Import our demo agents
from demo_agents import AgentOrchestrator, QuoteRequest, PriceRecommendation

# FastAPI app
app = FastAPI(
    title="Pricing Intelligence POC",
    description="Multi-Agent Pricing Intelligence System with FastAPI",
    version="1.0.0"
)

# Enable CORS for frontend integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize orchestrator
orchestrator = AgentOrchestrator()

# Pydantic models for API
class QuoteRequestAPI(BaseModel):
    product_id: str
    quantity: int
    customer_id: str
    product_family: str = "Software"
    region: str = "US"
    customer_segment: str = "Enterprise"

class PriceRecommendationAPI(BaseModel):
    recommended_price: float
    confidence: float
    win_probability: float
    explanation: str
    factors: Dict[str, Any]

class HealthResponse(BaseModel):
    status: str
    service: str
    version: str
    agents_status: Dict[str, str]

class ScoreRequest(BaseModel):
    product_id: str
    quantity: int
    proposed_price: float
    customer_segment: str = "Enterprise"
    region: str = "US"

class ScoreResponse(BaseModel):
    win_probability: float
    confidence: float
    expected_margin: float
    risk_level: str

class CurveRequest(BaseModel):
    product_id: str
    quantity: int
    customer_segment: str = "Enterprise"
    region: str = "US"
    price_range: Optional[int] = 10

class CurvePoint(BaseModel):
    price: float
    win_probability: float
    expected_revenue: float
    margin: float

class CurveResponse(BaseModel):
    optimal_price: float
    price_points: List[CurvePoint]

@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse(
        status="healthy",
        service="pricing-intelligence-api",
        version="1.0.0",
        agents_status={
            "rules": "active",
            "winrate": "active", 
            "elasticity": "active",
            "explainer": "active"
        }
    )

@app.post("/api/recommend", response_model=PriceRecommendationAPI)
async def get_price_recommendation(request: QuoteRequestAPI):
    """Get multi-agent price recommendation"""
    try:
        # Convert API request to internal format
        quote_request = QuoteRequest(
            product_id=request.product_id,
            quantity=request.quantity,
            customer_id=request.customer_id,
            product_family=request.product_family,
            region=request.region,
            customer_segment=request.customer_segment
        )
        
        # Get recommendation from orchestrator
        recommendation = orchestrator.get_price_recommendation(quote_request)
        
        # Convert to API response format
        return PriceRecommendationAPI(
            recommended_price=recommendation.recommended_price,
            confidence=recommendation.confidence,
            win_probability=recommendation.win_probability,
            explanation=recommendation.explanation,
            factors=recommendation.factors
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendation: {str(e)}")

@app.post("/api/score", response_model=ScoreResponse)
async def score_price(request: ScoreRequest):
    """Score a specific price proposal"""
    try:
        # Create context for scoring
        context = {
            "product_id": request.product_id,
            "quantity": request.quantity,
            "customer_segment": request.customer_segment,
            "region": request.region,
            "proposed_price": request.proposed_price,
            "base_price": orchestrator.product_data.get(request.product_id, {}).get("base_price", 100.0),
            "cost": orchestrator.product_data.get(request.product_id, {}).get("cost", 60.0)
        }
        
        # Get win rate prediction
        winrate_result = orchestrator.agents["winrate"].process(context)
        
        # Calculate expected margin
        margin = (request.proposed_price - context["cost"]) / request.proposed_price
        expected_margin = margin * winrate_result["win_probability"]
        
        # Determine risk level
        if winrate_result["win_probability"] > 0.7:
            risk_level = "low"
        elif winrate_result["win_probability"] > 0.4:
            risk_level = "medium"
        else:
            risk_level = "high"
        
        return ScoreResponse(
            win_probability=winrate_result["win_probability"],
            confidence=winrate_result["confidence"],
            expected_margin=expected_margin,
            risk_level=risk_level
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scoring price: {str(e)}")

@app.post("/api/curve", response_model=CurveResponse)
async def get_price_curve(request: CurveRequest):
    """Generate price-win probability curve"""
    try:
        # Get base product data
        product_data = orchestrator.product_data.get(request.product_id, {})
        base_price = product_data.get("base_price", 100.0)
        cost = product_data.get("cost", 60.0)
        
        # Generate price range
        min_price = base_price * 0.6  # 40% discount max
        max_price = base_price * 1.3  # 30% premium max
        price_range = request.price_range or 10
        step = (max_price - min_price) / (price_range - 1)
        
        price_points = []
        best_revenue = 0
        optimal_price = base_price
        
        for i in range(price_range):
            price = min_price + (i * step)
            
            # Create context for this price point
            context = {
                "product_id": request.product_id,
                "quantity": request.quantity,
                "customer_segment": request.customer_segment,
                "region": request.region,
                "proposed_price": price,
                "base_price": base_price,
                "cost": cost
            }
            
            # Get win rate for this price
            winrate_result = orchestrator.agents["winrate"].process(context)
            win_probability = winrate_result["win_probability"]
            
            # Calculate metrics
            margin = (price - cost) / price
            expected_revenue = price * win_probability * request.quantity
            
            # Track optimal price (max expected revenue)
            if expected_revenue > best_revenue:
                best_revenue = expected_revenue
                optimal_price = price
            
            price_points.append(CurvePoint(
                price=price,
                win_probability=win_probability,
                expected_revenue=expected_revenue,
                margin=margin
            ))
        
        return CurveResponse(
            optimal_price=optimal_price,
            price_points=price_points
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating price curve: {str(e)}")

@app.post("/api/feedback")
async def submit_feedback(feedback: Dict[str, Any]):
    """Submit feedback for model improvement (placeholder)"""
    # In a real system, this would store feedback for model retraining
    return {"status": "received", "message": "Feedback recorded for model improvement"}

if __name__ == "__main__":
    print("🚀 Starting Pricing Intelligence API Server")
    print("📊 Multi-Agent Architecture:")
    print("   • Rules Agent: Business policies and constraints")
    print("   • WinRate Agent: ML-powered win probability prediction")
    print("   • Elasticity Agent: Price sensitivity modeling")
    print("   • Explainer Agent: Natural language explanations")
    print("🌐 API Documentation: http://localhost:8000/docs")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8000)
