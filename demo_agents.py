"""
Simple test script to demonstrate the multi-agent pricing intelligence system
without external dependencies.
"""

import json
import sys
import os
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

# Add current directory to path for imports
sys.path.append(os.path.dirname(__file__))

@dataclass
class QuoteRequest:
    product_id: str
    quantity: int
    customer_id: str
    product_family: str = "Software"
    region: str = "US"
    customer_segment: str = "Enterprise"

@dataclass
class PriceRecommendation:
    recommended_price: float
    confidence: float
    win_probability: float
    explanation: str
    factors: Dict[str, Any]

class SimpleAgent:
    """Base agent class for the multi-agent system"""
    
    def __init__(self, name: str):
        self.name = name
        self.logger = SimpleLogger()
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        raise NotImplementedError

class SimpleLogger:
    """Simple logger replacement"""
    
    def info(self, message: str):
        print(f"[INFO] {datetime.now().strftime('%H:%M:%S')} - {message}")
    
    def warning(self, message: str):
        print(f"[WARN] {datetime.now().strftime('%H:%M:%S')} - {message}")

class RulesAgent(SimpleAgent):
    """Business rules agent - applies pricing policies"""
    
    def __init__(self):
        super().__init__("RulesAgent")
        # Simplified business rules
        self.policies = {
            "min_margin": 0.15,  # 15% minimum margin
            "max_discount": 0.30,  # 30% maximum discount
            "volume_tiers": {
                "small": (1, 10),
                "medium": (11, 100),
                "large": (101, 1000)
            }
        }
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Processing business rules for {context.get('product_id')}")
        
        quantity = context.get('quantity', 1)
        base_price = context.get('base_price', 100.0)
        
        # Determine volume tier
        if quantity <= 10:
            volume_tier = "small"
            volume_discount = 0.0
        elif quantity <= 100:
            volume_tier = "medium"
            volume_discount = 0.05
        else:
            volume_tier = "large"
            volume_discount = 0.10
        
        # Calculate pricing bounds
        min_price = base_price * (1 - self.policies["max_discount"])
        max_price = base_price * 1.2  # 20% premium max
        
        result = {
            "volume_tier": volume_tier,
            "volume_discount": volume_discount,
            "min_price": min_price,
            "max_price": max_price,
            "policy_bounds": {
                "min_margin": self.policies["min_margin"],
                "max_discount": self.policies["max_discount"]
            }
        }
        
        self.logger.info(f"Rules applied: {volume_tier} tier, {volume_discount:.1%} discount")
        return result

class WinRateAgent(SimpleAgent):
    """ML-powered win rate prediction agent"""
    
    def __init__(self):
        super().__init__("WinRateAgent")
        # Simplified model weights (normally trained ML model)
        self.feature_weights = {
            "price_competitiveness": -0.8,  # Lower price = higher win rate
            "customer_segment_enterprise": 0.3,
            "customer_segment_smb": -0.1,
            "volume_large": 0.4,
            "region_us": 0.1
        }
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Predicting win rate for {context.get('product_id')}")
        
        # Extract features
        proposed_price = context.get('proposed_price', 100.0)
        base_price = context.get('base_price', 100.0)
        customer_segment = context.get('customer_segment', 'Enterprise')
        volume_tier = context.get('volume_tier', 'small')
        region = context.get('region', 'US')
        
        # Calculate price competitiveness (simplified)
        price_ratio = proposed_price / base_price
        price_competitiveness = 1.0 - price_ratio  # Lower price = more competitive
        
        # Calculate features
        features = {
            "price_competitiveness": price_competitiveness,
            "customer_segment_enterprise": 1.0 if customer_segment == "Enterprise" else 0.0,
            "customer_segment_smb": 1.0 if customer_segment == "SMB" else 0.0,
            "volume_large": 1.0 if volume_tier == "large" else 0.0,
            "region_us": 1.0 if region == "US" else 0.0
        }
        
        # Simple linear model prediction
        score = sum(features[k] * self.feature_weights.get(k, 0) for k in features)
        win_probability = max(0.1, min(0.95, 1 / (1 + abs(score))))  # Sigmoid-like
        
        # Calculate confidence based on feature strength
        confidence = min(0.9, 0.5 + abs(score) * 0.2)
        
        result = {
            "win_probability": win_probability,
            "confidence": confidence,
            "features": features,
            "model_score": score
        }
        
        self.logger.info(f"Win probability: {win_probability:.1%} (confidence: {confidence:.1%})")
        return result

class ElasticityAgent(SimpleAgent):
    """Price elasticity and demand modeling agent"""
    
    def __init__(self):
        super().__init__("ElasticityAgent")
        # Simplified elasticity coefficients
        self.elasticity = -1.5  # Price elasticity of demand
        self.base_demand = 100  # Base demand units
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info(f"Analyzing price elasticity for {context.get('product_id')}")
        
        proposed_price = context.get('proposed_price', 100.0)
        base_price = context.get('base_price', 100.0)
        quantity = context.get('quantity', 1)
        
        # Calculate price change percentage
        price_change = (proposed_price - base_price) / base_price
        
        # Calculate demand impact using elasticity
        demand_change = self.elasticity * price_change
        expected_demand = self.base_demand * (1 + demand_change)
        
        # Calculate revenue impact
        revenue_at_base = base_price * self.base_demand
        revenue_at_proposed = proposed_price * expected_demand
        revenue_impact = (revenue_at_proposed - revenue_at_base) / revenue_at_base
        
        result = {
            "price_change_pct": price_change,
            "demand_change_pct": demand_change,
            "expected_demand": expected_demand,
            "revenue_impact_pct": revenue_impact,
            "elasticity_coefficient": self.elasticity,
            "optimal_price_indicator": "increase" if revenue_impact > 0 else "decrease"
        }
        
        self.logger.info(f"Revenue impact: {revenue_impact:.1%} from {price_change:.1%} price change")
        return result

class ExplainerAgent(SimpleAgent):
    """Natural language explanation agent"""
    
    def __init__(self):
        super().__init__("ExplainerAgent")
    
    def process(self, context: Dict[str, Any]) -> Dict[str, Any]:
        self.logger.info("Generating explanation for pricing recommendation")
        
        # Extract key metrics
        recommended_price = context.get('recommended_price', 0)
        base_price = context.get('base_price', 100)
        win_probability = context.get('win_probability', 0.5)
        volume_tier = context.get('volume_tier', 'small')
        revenue_impact = context.get('revenue_impact_pct', 0)
        
        # Calculate discount
        discount_pct = (base_price - recommended_price) / base_price
        
        # Generate explanation
        explanation_parts = []
        
        # Price positioning
        if discount_pct > 0.1:
            explanation_parts.append(f"Significant {discount_pct:.1%} discount from list price")
        elif discount_pct > 0:
            explanation_parts.append(f"Modest {discount_pct:.1%} discount applied")
        else:
            explanation_parts.append("Price at or above list price")
        
        # Volume consideration
        if volume_tier == "large":
            explanation_parts.append("Large volume tier qualifies for additional discounting")
        elif volume_tier == "medium":
            explanation_parts.append("Medium volume provides some pricing flexibility")
        
        # Win probability insight
        if win_probability > 0.7:
            explanation_parts.append(f"High win probability ({win_probability:.1%}) indicates competitive positioning")
        elif win_probability < 0.4:
            explanation_parts.append(f"Lower win probability ({win_probability:.1%}) suggests price may be too aggressive")
        
        # Revenue impact
        if revenue_impact > 0:
            explanation_parts.append(f"Expected to increase revenue by {revenue_impact:.1%}")
        elif revenue_impact < -0.05:
            explanation_parts.append(f"May reduce revenue by {abs(revenue_impact):.1%}")
        
        explanation = ". ".join(explanation_parts) + "."
        
        result = {
            "explanation": explanation,
            "key_factors": [
                f"Volume: {volume_tier}",
                f"Win Rate: {win_probability:.1%}",
                f"Discount: {discount_pct:.1%}",
                f"Revenue Impact: {revenue_impact:+.1%}"
            ]
        }
        
        self.logger.info("Explanation generated successfully")
        return result

class AgentOrchestrator:
    """Orchestrates the multi-agent pricing intelligence system"""
    
    def __init__(self):
        self.logger = SimpleLogger()
        self.agents = {
            "rules": RulesAgent(),
            "winrate": WinRateAgent(),
            "elasticity": ElasticityAgent(),
            "explainer": ExplainerAgent()
        }
        
        # Mock data for testing
        self.product_data = {
            "PROD-001": {"base_price": 100.0, "cost": 60.0, "family": "Software"},
            "PROD-002": {"base_price": 200.0, "cost": 120.0, "family": "Hardware"},
            "PROD-003": {"base_price": 50.0, "cost": 30.0, "family": "Service"}
        }
    
    def get_price_recommendation(self, request: QuoteRequest) -> PriceRecommendation:
        """Main orchestration method that coordinates all agents"""
        
        self.logger.info(f"Processing price recommendation for {request.product_id}")
        
        # Initialize context with request data
        context = {
            "product_id": request.product_id,
            "quantity": request.quantity,
            "customer_id": request.customer_id,
            "product_family": request.product_family,
            "region": request.region,
            "customer_segment": request.customer_segment,
            "base_price": self.product_data.get(request.product_id, {}).get("base_price", 100.0),
            "cost": self.product_data.get(request.product_id, {}).get("cost", 60.0)
        }
        
        # Step 1: Apply business rules
        rules_result = self.agents["rules"].process(context)
        context.update(rules_result)
        
        # Step 2: Generate price candidates
        price_candidates = self._generate_price_candidates(context)
        
        # Step 3: Evaluate each candidate with ML agents
        best_price = price_candidates[0] if price_candidates else context["base_price"]
        best_score = -1
        best_context = context.copy()
        
        for candidate_price in price_candidates:
            candidate_context = context.copy()
            candidate_context["proposed_price"] = candidate_price
            
            # Get win rate prediction
            winrate_result = self.agents["winrate"].process(candidate_context)
            candidate_context.update(winrate_result)
            
            # Get elasticity analysis
            elasticity_result = self.agents["elasticity"].process(candidate_context)
            candidate_context.update(elasticity_result)
            
            # Calculate composite score (expected margin)
            margin = (candidate_price - context["cost"]) / candidate_price
            expected_margin = margin * winrate_result["win_probability"]
            
            if expected_margin > best_score:
                best_score = expected_margin
                best_price = candidate_price
                best_context = candidate_context
        
        # Step 4: Generate explanation
        best_context["recommended_price"] = best_price
        explanation_result = self.agents["explainer"].process(best_context)
        
        # Create final recommendation
        recommendation = PriceRecommendation(
            recommended_price=best_price,
            confidence=best_context.get("confidence", 0.5),
            win_probability=best_context.get("win_probability", 0.5),
            explanation=explanation_result["explanation"],
            factors={
                "volume_tier": best_context.get("volume_tier", "small"),
                "expected_margin": best_score,
                "revenue_impact": best_context.get("revenue_impact_pct", 0.0),
                "key_factors": explanation_result["key_factors"]
            }
        )
        
        self.logger.info(f"Recommendation complete: ${best_price:.2f} (margin: {best_score:.1%})")
        return recommendation
    
    def _generate_price_candidates(self, context: Dict[str, Any]) -> List[float]:
        """Generate price candidates within policy bounds"""
        
        base_price = context["base_price"]
        min_price = context["min_price"]
        max_price = context["max_price"]
        volume_discount = context["volume_discount"]
        
        # Start with volume-discounted price
        anchor_price = base_price * (1 - volume_discount)
        
        # Generate candidates around the anchor
        candidates = [
            anchor_price,  # Anchor price
            anchor_price * 0.95,  # 5% below anchor
            anchor_price * 0.90,  # 10% below anchor
            anchor_price * 1.05,  # 5% above anchor
        ]
        
        # Filter to policy bounds
        candidates = [p for p in candidates if min_price <= p <= max_price]
        
        # Ensure we have at least min and max price
        if min_price not in candidates:
            candidates.append(min_price)
        if max_price not in candidates:
            candidates.append(max_price)
        
        return sorted(set(candidates))

def demo_multi_agent_system():
    """Demonstrate the multi-agent pricing intelligence system"""
    
    print("🤖 Multi-Agent Pricing Intelligence Demo")
    print("=" * 50)
    
    # Initialize orchestrator
    orchestrator = AgentOrchestrator()
    
    # Test scenarios
    scenarios = [
        QuoteRequest(
            product_id="PROD-001",
            quantity=5,
            customer_id="CUST-001",
            customer_segment="Enterprise",
            region="US"
        ),
        QuoteRequest(
            product_id="PROD-002", 
            quantity=150,
            customer_id="CUST-002",
            customer_segment="SMB",
            region="EU"
        ),
        QuoteRequest(
            product_id="PROD-003",
            quantity=25,
            customer_id="CUST-003",
            customer_segment="Enterprise",
            region="APAC"
        )
    ]
    
    for i, scenario in enumerate(scenarios, 1):
        print(f"\n📋 Scenario {i}: {scenario.product_id}")
        print(f"   Quantity: {scenario.quantity}, Customer: {scenario.customer_segment}, Region: {scenario.region}")
        print("-" * 50)
        
        # Get recommendation
        recommendation = orchestrator.get_price_recommendation(scenario)
        
        # Display results
        print(f"\n💰 Recommended Price: ${recommendation.recommended_price:.2f}")
        print(f"🎯 Win Probability: {recommendation.win_probability:.1%}")
        print(f"📊 Confidence: {recommendation.confidence:.1%}")
        print(f"\n📝 Explanation:")
        print(f"   {recommendation.explanation}")
        print(f"\n🔍 Key Factors:")
        for factor in recommendation.factors["key_factors"]:
            print(f"   • {factor}")
        
        print("\n" + "=" * 50)
    
    print("\n✅ Multi-agent system demonstration complete!")
    print("\nThis showcases how multiple AI agents work together:")
    print("• Rules Agent: Applies business policies and constraints") 
    print("• WinRate Agent: Predicts probability of winning the deal")
    print("• Elasticity Agent: Models price sensitivity and revenue impact")
    print("• Explainer Agent: Generates human-readable explanations")
    print("• Orchestrator: Coordinates agents and optimizes for expected margin")

if __name__ == "__main__":
    demo_multi_agent_system()
