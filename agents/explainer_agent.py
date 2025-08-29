from .base_agent import BaseAgent
from typing import Dict, Any, List
import re

class ExplainerAgent(BaseAgent):
    """Agent that generates natural language explanations for pricing decisions"""
    
    def __init__(self):
        super().__init__("ExplainerAgent")
        
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate explanation for pricing recommendation"""
        
        # Extract key information
        floor = context.get('floor_price', 0)
        target = context.get('target_price', 0)
        stretch = context.get('stretch_price', 0)
        win_prob = context.get('win_probability', 0)
        elasticity = context.get('price_elasticity', 0)
        segment = context.get('customer_segment', 'Unknown')
        region = context.get('region', 'Unknown')
        
        # Generate natural language explanation
        explanation_parts = []
        
        # Price positioning
        if target > 0:
            margin = ((target - context.get('cogs', target * 0.7)) / context.get('cogs', target * 0.7)) * 100
            explanation_parts.append(f"The target price of ${target:.2f} delivers a {margin:.1f}% margin.")
        
        # Win probability insight
        if win_prob > 0.7:
            explanation_parts.append(f"This price has a strong {win_prob:.0%} probability of winning.")
        elif win_prob > 0.4:
            explanation_parts.append(f"This price has a moderate {win_prob:.0%} chance of success.")
        else:
            explanation_parts.append(f"This price has a lower {win_prob:.0%} win probability - consider the floor price.")
        
        # Elasticity insight
        if elasticity < -1.5:
            explanation_parts.append(f"The {segment} segment in {region} is price-sensitive (elasticity: {elasticity:.1f}), so small price changes have big impact.")
        elif elasticity > -1.0:
            explanation_parts.append(f"This customer segment shows low price sensitivity (elasticity: {elasticity:.1f}), allowing for premium pricing.")
        else:
            explanation_parts.append(f"Price sensitivity is moderate (elasticity: {elasticity:.1f}) for this segment.")
        
        # Competitive positioning
        competitor_price = context.get('competitor_price')
        if competitor_price and target > 0:
            price_diff_pct = ((target - competitor_price) / competitor_price) * 100
            if abs(price_diff_pct) < 5:
                explanation_parts.append("Our price closely matches competitor pricing.")
            elif price_diff_pct > 10:
                explanation_parts.append(f"We're pricing {price_diff_pct:.1f}% above competitors - justify with value proposition.")
            elif price_diff_pct < -10:
                explanation_parts.append(f"We're {abs(price_diff_pct):.1f}% below competitors - opportunity for margin improvement.")
        
        # Volume considerations
        quantity = context.get('quantity', 0)
        if quantity > 20:
            explanation_parts.append("Large volume order - consider additional discount for strategic value.")
        elif quantity < 5:
            explanation_parts.append("Small volume - premium pricing acceptable.")
        
        # Channel insights
        channel = context.get('channel', '')
        if channel.lower() == 'direct':
            explanation_parts.append("Direct sales channel allows for relationship-based pricing.")
        elif channel.lower() == 'partner':
            explanation_parts.append("Partner channel requires competitive pricing for reseller margins.")
        
        # Policy compliance
        approval_band = context.get('approval_band', 'UNKNOWN')
        if approval_band == 'APPROVED':
            explanation_parts.append("Price meets all policy requirements for automatic approval.")
        elif approval_band == 'REVIEW':
            explanation_parts.append("Price requires management review due to policy thresholds.")
        elif approval_band == 'REJECT':
            explanation_parts.append("Price below policy minimums - requires special approval.")
        
        # Risk factors
        risk_factors = []
        if win_prob < 0.3:
            risk_factors.append("low win probability")
        if elasticity < -2.0:
            risk_factors.append("high price sensitivity")
        if context.get('margin_pct', 0) < 0.1:
            risk_factors.append("thin margins")
        
        if risk_factors:
            explanation_parts.append(f"Key risks: {', '.join(risk_factors)}.")
        
        # Recommendations
        recommendations = []
        if win_prob < 0.4 and target > floor:
            recommendations.append("Consider lowering price toward floor for better win rate")
        if elasticity < -1.5 and target > context.get('current_price', target):
            recommendations.append("Price increase risky due to high elasticity")
        if quantity > 30:
            recommendations.append("Evaluate volume discount for strategic relationship")
        
        # Combine into coherent explanation
        main_explanation = " ".join(explanation_parts)
        
        result = {
            'explanation': main_explanation,
            'recommendations': recommendations,
            'key_insights': [
                f"Win probability: {win_prob:.0%}",
                f"Price elasticity: {elasticity:.2f}",
                f"Approval status: {approval_band}"
            ],
            'reasons': [
                "AI-generated explanation combining multiple models",
                "Considers pricing, elasticity, competition, and policy",
                "Tailored for sales team consumption"
            ]
        }
        
        self.log_execution(context, result)
        return result
    
    def explain_comparison(self, scenario_a: Dict, scenario_b: Dict) -> str:
        """Compare two pricing scenarios and explain differences"""
        price_diff = scenario_b.get('target_price', 0) - scenario_a.get('target_price', 0)
        win_diff = scenario_b.get('win_probability', 0) - scenario_a.get('win_probability', 0)
        
        explanation = f"Increasing price by ${price_diff:.2f} "
        if win_diff > 0:
            explanation += f"improves win probability by {win_diff:+.1%}"
        else:
            explanation += f"reduces win probability by {abs(win_diff):.1%}"
        
        return explanation
    
    def generate_seller_talking_points(self, context: Dict[str, Any]) -> List[str]:
        """Generate talking points for sales conversations"""
        talking_points = []
        
        target = context.get('target_price', 0)
        win_prob = context.get('win_probability', 0)
        competitor_price = context.get('competitor_price', 0)
        
        # Value justification
        if competitor_price and target > competitor_price:
            talking_points.append(f"Our solution offers premium value - price reflects quality and service superiority")
        
        # Volume incentives
        quantity = context.get('quantity', 0)
        if quantity > 15:
            talking_points.append(f"This volume ({quantity} units) qualifies for our preferred customer pricing")
        
        # Urgency/scarcity
        if win_prob > 0.6:
            talking_points.append("This price point has been successful with similar customers in your industry")
        
        # Partnership angle
        segment = context.get('customer_segment', '')
        if segment == 'Enterprise':
            talking_points.append("As an enterprise partner, you have access to our strategic pricing program")
        
        return talking_points
