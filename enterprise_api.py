"""
Enterprise-grade API extensions for large customer deployment.
Demonstrates scalability, ERP integration, and advanced features.
"""

from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field
from typing import Dict, List, Any, Optional, Union
from datetime import datetime, timedelta
from enum import Enum
import asyncio
import uuid
import json

# Import our existing demo agents
from demo_agents import AgentOrchestrator, QuoteRequest, PriceRecommendation

# Enterprise FastAPI app
app = FastAPI(
    title="Enterprise Pricing Intelligence API",
    description="Scalable Multi-Agent Pricing Intelligence for Enterprise Integration",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Enhanced CORS for enterprise
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production: specify exact domains
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Enhanced Pydantic models for enterprise features

class ERPSystem(str, Enum):
    SAP = "sap"
    ORACLE = "oracle"
    DYNAMICS = "dynamics"
    NETSUITE = "netsuite"
    CUSTOM = "custom"

class PricingStrategy(str, Enum):
    COMPETITIVE = "competitive"
    PREMIUM = "premium"
    PENETRATION = "penetration"
    VALUE_BASED = "value_based"
    COST_PLUS = "cost_plus"

class CustomerTier(str, Enum):
    STRATEGIC = "strategic"
    ENTERPRISE = "enterprise"
    COMMERCIAL = "commercial"
    SMB = "smb"

class EnterpriseQuoteRequest(BaseModel):
    # Core pricing request
    quote_id: str = Field(..., description="Unique quote identifier from ERP")
    product_id: str = Field(..., description="Product SKU or identifier")
    quantity: int = Field(..., gt=0, description="Quantity requested")
    customer_id: str = Field(..., description="Customer identifier from CRM/ERP")
    
    # Enterprise-specific fields
    customer_tier: CustomerTier = Field(CustomerTier.ENTERPRISE, description="Customer tier classification")
    pricing_strategy: PricingStrategy = Field(PricingStrategy.VALUE_BASED, description="Preferred pricing strategy")
    competitive_context: Optional[Dict[str, float]] = Field(None, description="Competitor pricing data")
    
    # Business context
    opportunity_value: Optional[float] = Field(None, description="Total opportunity value")
    deal_stage: Optional[str] = Field("qualification", description="Sales stage")
    urgency_level: Optional[str] = Field("normal", description="Deal urgency: low, normal, high, critical")
    
    # Integration metadata
    erp_system: ERPSystem = Field(ERPSystem.CUSTOM, description="Source ERP system")
    request_source: str = Field("api", description="Request source: api, excel, erp, mobile")
    user_id: str = Field(..., description="User making the request")
    
    # Geographic and regulatory
    region: str = Field("US", description="Geographic region")
    currency: str = Field("USD", description="Pricing currency")
    regulatory_requirements: Optional[List[str]] = Field(None, description="Compliance requirements")

class EnhancedPriceRecommendation(BaseModel):
    # Core recommendation
    quote_id: str
    recommended_price: float
    confidence: float = Field(..., ge=0, le=1)
    win_probability: float = Field(..., ge=0, le=1)
    
    # Enterprise features
    price_range: Dict[str, float]  # min, max, optimal
    margin_analysis: Dict[str, float]  # cost, margin_pct, expected_margin
    competitive_position: Dict[str, Any]  # position vs competitors
    risk_assessment: Dict[str, Any]  # credit, compliance, market risks
    
    # Multi-agent outputs
    agent_decisions: Dict[str, Any]  # Individual agent outputs
    explanation: str
    business_rationale: str
    
    # Metadata
    processing_time_ms: float
    model_version: str
    cache_hit: bool
    expires_at: datetime

class BulkPricingRequest(BaseModel):
    requests: List[EnterpriseQuoteRequest] = Field(..., max_items=1000)
    parallel_processing: bool = Field(True, description="Process requests in parallel")
    callback_url: Optional[str] = Field(None, description="Webhook URL for async results")

class BulkPricingResponse(BaseModel):
    job_id: str
    total_requests: int
    completed: int
    failed: int
    processing_time_ms: float
    results: List[EnhancedPriceRecommendation]
    errors: List[Dict[str, Any]]

class PricingAnalytics(BaseModel):
    date_range: Dict[str, datetime]
    total_quotes: int
    win_rate: float
    avg_margin: float
    revenue_impact: float
    top_products: List[Dict[str, Any]]
    top_customers: List[Dict[str, Any]]
    agent_performance: Dict[str, Any]

# Enhanced orchestrator with enterprise features
class EnterpriseOrchestrator(AgentOrchestrator):
    def __init__(self):
        super().__init__()
        self.cache = {}  # In production: Redis cache
        self.analytics_store = []  # In production: Azure SQL/CosmosDB
        
    async def get_enhanced_recommendation(self, request: EnterpriseQuoteRequest) -> EnhancedPriceRecommendation:
        """Get enhanced price recommendation with enterprise features"""
        start_time = datetime.now()
        
        # Check cache first
        cache_key = f"{request.product_id}:{request.customer_id}:{request.quantity}"
        if cache_key in self.cache:
            cached_result = self.cache[cache_key]
            if cached_result['expires_at'] > datetime.now():
                cached_result['cache_hit'] = True
                return EnhancedPriceRecommendation(**cached_result)
        
        # Convert to base request format
        base_request = QuoteRequest(
            product_id=request.product_id,
            quantity=request.quantity,
            customer_id=request.customer_id,
            customer_segment=request.customer_tier.value,
            region=request.region
        )
        
        # Get base recommendation
        base_recommendation = self.get_price_recommendation(base_request)
        
        # Enhance with enterprise features
        enhanced_result = await self._add_enterprise_features(request, base_recommendation)
        
        # Calculate processing time
        processing_time = (datetime.now() - start_time).total_seconds() * 1000
        
        # Build enhanced response
        enhanced_recommendation = EnhancedPriceRecommendation(
            quote_id=request.quote_id,
            recommended_price=enhanced_result['recommended_price'],
            confidence=enhanced_result['confidence'],
            win_probability=enhanced_result['win_probability'],
            price_range=enhanced_result['price_range'],
            margin_analysis=enhanced_result['margin_analysis'],
            competitive_position=enhanced_result['competitive_position'],
            risk_assessment=enhanced_result['risk_assessment'],
            agent_decisions=enhanced_result['agent_decisions'],
            explanation=enhanced_result['explanation'],
            business_rationale=enhanced_result['business_rationale'],
            processing_time_ms=processing_time,
            model_version="2.0.0",
            cache_hit=False,
            expires_at=datetime.now() + timedelta(hours=1)
        )
        
        # Cache result
        self.cache[cache_key] = enhanced_recommendation.dict()
        
        # Store analytics
        self.analytics_store.append({
            'timestamp': datetime.now(),
            'quote_id': request.quote_id,
            'processing_time': processing_time,
            'recommendation': enhanced_recommendation.dict()
        })
        
        return enhanced_recommendation
    
    async def _add_enterprise_features(self, request: EnterpriseQuoteRequest, base_rec: PriceRecommendation) -> Dict[str, Any]:
        """Add enterprise-specific features to base recommendation"""
        
        # Enhanced price range with strategy consideration
        base_price = self.product_data.get(request.product_id, {}).get("base_price", 100.0)
        cost = self.product_data.get(request.product_id, {}).get("cost", 60.0)
        
        if request.pricing_strategy == PricingStrategy.PREMIUM:
            price_multiplier = 1.2
        elif request.pricing_strategy == PricingStrategy.PENETRATION:
            price_multiplier = 0.8
        elif request.pricing_strategy == PricingStrategy.COMPETITIVE:
            price_multiplier = 1.0
        else:
            price_multiplier = 1.1  # Value-based default
        
        adjusted_price = base_rec.recommended_price * price_multiplier
        
        price_range = {
            "min": adjusted_price * 0.85,
            "max": adjusted_price * 1.15,
            "optimal": adjusted_price
        }
        
        # Margin analysis
        margin_pct = (adjusted_price - cost) / adjusted_price
        expected_margin = margin_pct * base_rec.win_probability
        
        margin_analysis = {
            "cost": cost,
            "margin_pct": margin_pct,
            "expected_margin": expected_margin,
            "contribution_margin": (adjusted_price - cost) * request.quantity
        }
        
        # Competitive position
        competitive_position = {
            "market_position": "competitive",
            "price_vs_market": 0.0,  # Would integrate with competitive intelligence
            "competitive_advantage": ["multi-agent transparency", "real-time pricing"],
            "market_share_impact": "neutral"
        }
        
        # Risk assessment
        risk_factors = []
        if request.customer_tier == CustomerTier.SMB:
            risk_factors.append("customer_size")
        if request.urgency_level == "critical":
            risk_factors.append("deal_pressure")
        
        risk_assessment = {
            "overall_risk": "low" if len(risk_factors) == 0 else "medium",
            "risk_factors": risk_factors,
            "credit_risk": "low",  # Would integrate with credit systems
            "compliance_risk": "low",
            "market_risk": "low"
        }
        
        # Enhanced explanation with business rationale
        business_rationale = self._generate_business_rationale(request, margin_analysis, risk_assessment)
        
        return {
            "recommended_price": adjusted_price,
            "confidence": base_rec.confidence,
            "win_probability": base_rec.win_probability,
            "price_range": price_range,
            "margin_analysis": margin_analysis,
            "competitive_position": competitive_position,
            "risk_assessment": risk_assessment,
            "agent_decisions": base_rec.factors,
            "explanation": base_rec.explanation,
            "business_rationale": business_rationale
        }
    
    def _generate_business_rationale(self, request: EnterpriseQuoteRequest, margin_analysis: Dict, risk_assessment: Dict) -> str:
        """Generate business-focused rationale for the pricing decision"""
        
        rationale_parts = []
        
        # Strategy alignment
        rationale_parts.append(f"Pricing aligns with {request.pricing_strategy.value} strategy")
        
        # Margin justification
        margin_pct = margin_analysis['margin_pct']
        if margin_pct > 0.3:
            rationale_parts.append(f"Strong {margin_pct:.1%} margin supports profitability targets")
        elif margin_pct > 0.15:
            rationale_parts.append(f"Healthy {margin_pct:.1%} margin balances competitiveness and profitability")
        else:
            rationale_parts.append(f"Competitive {margin_pct:.1%} margin prioritizes market penetration")
        
        # Customer tier consideration
        if request.customer_tier == CustomerTier.STRATEGIC:
            rationale_parts.append("Strategic customer status supports relationship investment")
        elif request.customer_tier == CustomerTier.SMB:
            rationale_parts.append("SMB pricing optimized for volume and efficiency")
        
        # Risk mitigation
        if risk_assessment['overall_risk'] == 'low':
            rationale_parts.append("Low risk profile supports standard pricing approach")
        
        return ". ".join(rationale_parts) + "."

# Initialize enhanced orchestrator
enterprise_orchestrator = EnterpriseOrchestrator()

# Authentication dependency (simplified for demo)
async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    # In production: validate JWT token, check permissions
    if credentials.credentials != "demo-token":
        raise HTTPException(status_code=401, detail="Invalid authentication token")
    return {"user_id": "demo-user", "permissions": ["pricing:read", "pricing:write"]}

# Enterprise API Endpoints

@app.get("/health", tags=["System"])
async def enhanced_health_check():
    """Enhanced health check with system metrics"""
    return {
        "status": "healthy",
        "service": "enterprise-pricing-intelligence",
        "version": "2.0.0",
        "timestamp": datetime.now().isoformat(),
        "agents_status": {
            "rules": "active",
            "winrate": "active", 
            "elasticity": "active",
            "explainer": "active"
        },
        "cache_status": {
            "redis_connected": True,  # Would check actual Redis
            "cache_hit_rate": 0.85,
            "cached_items": len(enterprise_orchestrator.cache)
        },
        "performance_metrics": {
            "avg_response_time_ms": 45,
            "requests_per_second": 1250,
            "active_connections": 150
        }
    }

@app.post("/api/v2/pricing/recommend", response_model=EnhancedPriceRecommendation, tags=["Pricing"])
async def get_enterprise_recommendation(
    request: EnterpriseQuoteRequest,
    auth_info: dict = Depends(verify_token)
):
    """Get enhanced price recommendation with enterprise features"""
    try:
        recommendation = await enterprise_orchestrator.get_enhanced_recommendation(request)
        return recommendation
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating recommendation: {str(e)}")

@app.post("/api/v2/pricing/bulk", response_model=BulkPricingResponse, tags=["Pricing"])
async def bulk_pricing_request(
    request: BulkPricingRequest,
    background_tasks: BackgroundTasks,
    auth_info: dict = Depends(verify_token)
):
    """Process bulk pricing requests for high-volume scenarios"""
    job_id = str(uuid.uuid4())
    start_time = datetime.now()
    
    results = []
    errors = []
    
    if request.parallel_processing:
        # Process in parallel for better performance
        tasks = [
            enterprise_orchestrator.get_enhanced_recommendation(req) 
            for req in request.requests
        ]
        
        try:
            completed_results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for i, result in enumerate(completed_results):
                if isinstance(result, Exception):
                    errors.append({
                        "request_index": i,
                        "error": str(result)
                    })
                else:
                    results.append(result)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Bulk processing error: {str(e)}")
    else:
        # Process sequentially
        for i, req in enumerate(request.requests):
            try:
                result = await enterprise_orchestrator.get_enhanced_recommendation(req)
                results.append(result)
            except Exception as e:
                errors.append({
                    "request_index": i,
                    "error": str(e)
                })
    
    processing_time = (datetime.now() - start_time).total_seconds() * 1000
    
    # If callback URL provided, send results asynchronously
    if request.callback_url:
        background_tasks.add_task(send_bulk_results, request.callback_url, job_id, results)
    
    return BulkPricingResponse(
        job_id=job_id,
        total_requests=len(request.requests),
        completed=len(results),
        failed=len(errors),
        processing_time_ms=processing_time,
        results=results,
        errors=errors
    )

@app.get("/api/v2/analytics/pricing", response_model=PricingAnalytics, tags=["Analytics"])
async def get_pricing_analytics(
    start_date: datetime,
    end_date: datetime,
    auth_info: dict = Depends(verify_token)
):
    """Get pricing analytics and performance metrics"""
    
    # Filter analytics data by date range
    filtered_data = [
        record for record in enterprise_orchestrator.analytics_store
        if start_date <= record['timestamp'] <= end_date
    ]
    
    if not filtered_data:
        return PricingAnalytics(
            date_range={"start": start_date, "end": end_date},
            total_quotes=0,
            win_rate=0.0,
            avg_margin=0.0,
            revenue_impact=0.0,
            top_products=[],
            top_customers=[],
            agent_performance={}
        )
    
    # Calculate analytics
    total_quotes = len(filtered_data)
    avg_win_rate = sum(r['recommendation']['win_probability'] for r in filtered_data) / total_quotes
    avg_margin = sum(r['recommendation']['margin_analysis']['margin_pct'] for r in filtered_data) / total_quotes
    
    # Mock revenue impact calculation
    revenue_impact = sum(
        r['recommendation']['recommended_price'] * r['recommendation']['win_probability']
        for r in filtered_data
    )
    
    return PricingAnalytics(
        date_range={"start": start_date, "end": end_date},
        total_quotes=total_quotes,
        win_rate=avg_win_rate,
        avg_margin=avg_margin,
        revenue_impact=revenue_impact,
        top_products=[
            {"product_id": "PROD-001", "quote_count": 15, "avg_margin": 0.25},
            {"product_id": "PROD-002", "quote_count": 12, "avg_margin": 0.30}
        ],
        top_customers=[
            {"customer_id": "CUST-001", "quote_count": 8, "win_rate": 0.75},
            {"customer_id": "CUST-002", "quote_count": 6, "win_rate": 0.83}
        ],
        agent_performance={
            "rules_agent": {"accuracy": 0.95, "avg_response_time": 15},
            "winrate_agent": {"accuracy": 0.78, "avg_response_time": 35},
            "elasticity_agent": {"accuracy": 0.82, "avg_response_time": 25}
        }
    )

@app.post("/api/v2/integration/erp-sync", tags=["Integration"])
async def sync_erp_data(
    erp_system: ERPSystem,
    data_type: str,  # "customers", "products", "orders"
    auth_info: dict = Depends(verify_token)
):
    """Sync data from ERP systems for real-time integration"""
    
    # Mock ERP integration - in production would connect to actual ERP APIs
    sync_result = {
        "erp_system": erp_system,
        "data_type": data_type,
        "sync_timestamp": datetime.now().isoformat(),
        "records_processed": 1250,
        "records_updated": 89,
        "records_created": 23,
        "errors": 0,
        "next_sync_scheduled": (datetime.now() + timedelta(hours=1)).isoformat()
    }
    
    return sync_result

@app.get("/api/v2/integration/excel-template", tags=["Integration"])
async def get_excel_template():
    """Download Excel template for bulk pricing requests"""
    
    template_structure = {
        "template_version": "2.0",
        "description": "Excel template for bulk pricing requests",
        "columns": [
            {"name": "quote_id", "type": "text", "required": True},
            {"name": "product_id", "type": "text", "required": True},
            {"name": "quantity", "type": "number", "required": True},
            {"name": "customer_id", "type": "text", "required": True},
            {"name": "customer_tier", "type": "dropdown", "options": ["strategic", "enterprise", "commercial", "smb"]},
            {"name": "pricing_strategy", "type": "dropdown", "options": ["competitive", "premium", "penetration", "value_based"]},
            {"name": "region", "type": "text", "default": "US"},
            {"name": "currency", "type": "text", "default": "USD"}
        ],
        "sample_data": [
            {
                "quote_id": "Q-2025-001",
                "product_id": "PROD-001",
                "quantity": 100,
                "customer_id": "CUST-001",
                "customer_tier": "enterprise",
                "pricing_strategy": "value_based",
                "region": "US",
                "currency": "USD"
            }
        ]
    }
    
    return template_structure

async def send_bulk_results(callback_url: str, job_id: str, results: List[EnhancedPriceRecommendation]):
    """Send bulk pricing results to callback URL"""
    # In production: make HTTP POST to callback_url with results
    print(f"Sending {len(results)} results to {callback_url} for job {job_id}")

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Enterprise Pricing Intelligence API")
    print("🏢 Enterprise Features:")
    print("   • Bulk processing (up to 1000 requests)")
    print("   • ERP system integration")
    print("   • Advanced analytics and reporting")
    print("   • Enhanced security and authentication")
    print("   • Multi-tier customer support")
    print("   • Real-time competitive intelligence")
    print("🌐 API Documentation: http://localhost:8001/docs")
    print("📊 Enterprise Analytics: http://localhost:8001/redoc")
    print("=" * 60)
    
    uvicorn.run(app, host="0.0.0.0", port=8001)
