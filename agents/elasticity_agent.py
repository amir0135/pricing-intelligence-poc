from .base_agent import BaseAgent
from typing import Dict, Any
import numpy as np

class ElasticityAgent(BaseAgent):
    """Agent that estimates price elasticity using econometric models"""
    
    def __init__(self):
        super().__init__("ElasticityAgent")
        # Elasticity parameters by segment and region (simplified)
        self.elasticity_params = {
            ('Enterprise', 'EMEA'): {'base_elasticity': -1.2, 'volume_adj': 0.1},
            ('Enterprise', 'Americas'): {'base_elasticity': -1.1, 'volume_adj': 0.12},
            ('SMB', 'EMEA'): {'base_elasticity': -1.8, 'volume_adj': 0.05},
            ('SMB', 'Americas'): {'base_elasticity': -1.7, 'volume_adj': 0.08},
        }
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate price elasticity and demand impact"""
        segment = context.get('customer_segment', 'Enterprise')
        region = context.get('region', 'EMEA')
        current_price = context.get('current_price', context.get('target_price', 100))
        proposed_price = context.get('proposed_price', current_price)
        quantity = context.get('quantity', 10)
        
        # Get elasticity parameters
        key = (segment, region)
        if key in self.elasticity_params:
            params = self.elasticity_params[key]
        else:
            # Default fallback
            params = {'base_elasticity': -1.5, 'volume_adj': 0.08}
        
        base_elasticity = params['base_elasticity']
        volume_adj = params['volume_adj']
        
        # Adjust elasticity based on volume (larger volumes = less elastic)
        volume_factor = min(1.0, quantity / 20.0)  # Normalize to 20 units
        adjusted_elasticity = base_elasticity * (1 - volume_factor * volume_adj)
        
        # Calculate price change impact
        price_change_pct = (proposed_price - current_price) / current_price if current_price > 0 else 0
        demand_change_pct = adjusted_elasticity * price_change_pct
        
        # Estimate new quantity
        new_quantity = quantity * (1 + demand_change_pct)
        new_quantity = max(1, new_quantity)  # Minimum 1 unit
        
        # Revenue impact
        current_revenue = current_price * quantity
        new_revenue = proposed_price * new_quantity
        revenue_change_pct = (new_revenue - current_revenue) / current_revenue if current_revenue > 0 else 0
        
        # Optimal price calculation (simplified)
        # For monopolistic competition: P_optimal = MC / (1 + 1/elasticity)
        cogs = context.get('cogs', current_price * 0.7)
        if adjusted_elasticity < -1:  # Elastic demand
            optimal_markup = -1 / (adjusted_elasticity + 1)
            suggested_price = cogs / (1 - optimal_markup)
        else:
            suggested_price = current_price  # Inelastic, keep current
        
        result = {
            'price_elasticity': round(adjusted_elasticity, 2),
            'demand_change_pct': round(demand_change_pct, 3),
            'new_quantity_estimate': round(new_quantity, 1),
            'revenue_change_pct': round(revenue_change_pct, 3),
            'suggested_price': round(suggested_price, 2),
            'elasticity_segment': f"{segment}-{region}",
            'reasons': [
                f"Price elasticity: {adjusted_elasticity:.2f}",
                f"Demand impact: {demand_change_pct:+.1%}",
                f"Revenue impact: {revenue_change_pct:+.1%}"
            ]
        }
        
        self.log_execution(context, result)
        return result
    
    def get_demand_curve(self, context: Dict[str, Any], price_range: list) -> list:
        """Generate demand curve points"""
        curve_points = []
        base_quantity = context.get('quantity', 10)
        base_price = price_range[len(price_range)//2]  # Middle price as base
        
        for price in price_range:
            price_context = context.copy()
            price_context['current_price'] = base_price
            price_context['proposed_price'] = price
            
            result = self.execute(price_context)
            curve_points.append({
                'price': round(price, 2),
                'quantity': result['new_quantity_estimate'],
                'revenue': round(price * result['new_quantity_estimate'], 2)
            })
        
        return curve_points
