from typing import Dict, Any, List
from .rules_agent import RulesAgent
from .winrate_agent import WinRateAgent
from .elasticity_agent import ElasticityAgent
from .explainer_agent import ExplainerAgent
from loguru import logger
import numpy as np
import pandas as pd
from pathlib import Path

class AgentOrchestrator:
    """Orchestrates multiple pricing agents to provide comprehensive recommendations"""
    
    def __init__(self):
        self.rules_agent = RulesAgent()
        self.winrate_agent = WinRateAgent()
        self.elasticity_agent = ElasticityAgent()
        self.explainer_agent = ExplainerAgent()
        
        # Load supporting data
        self._load_data()
    
    def _load_data(self):
        """Load reference data for context enrichment"""
        data_dir = Path(__file__).parent.parent / "data" / "sample_csv"
        
        try:
            self.products_df = pd.read_csv(data_dir / "products.csv")
            self.customers_df = pd.read_csv(data_dir / "customers.csv")
            self.cogs_df = pd.read_csv(data_dir / "cogs.csv")
        except Exception as e:
            logger.warning(f"Could not load reference data: {e}")
            self.products_df = pd.DataFrame()
            self.customers_df = pd.DataFrame()
            self.cogs_df = pd.DataFrame()
    
    def _enrich_context(self, sku: str, customer_id: str, quantity: int, 
                       country: str, channel: str, currency: str) -> Dict[str, Any]:
        """Enrich request context with additional data"""
        context = {
            'sku': sku,
            'customer_id': customer_id,
            'quantity': quantity,
            'country': country,
            'channel': channel,
            'currency': currency
        }
        
        # Add product data
        if not self.products_df.empty:
            product_row = self.products_df[self.products_df['sku'] == sku]
            if not product_row.empty:
                context['product_id'] = product_row.iloc[0]['product_id']
                context['product_family'] = product_row.iloc[0]['family']
                
                # Add COGS
                product_id = context['product_id']
                if not self.cogs_df.empty:
                    cogs_row = self.cogs_df[self.cogs_df['product_id'] == product_id]
                    if not cogs_row.empty:
                        context['cogs'] = float(cogs_row.iloc[0]['cogs'])
        
        # Add customer data
        if not self.customers_df.empty:
            customer_row = self.customers_df[self.customers_df['customer_id'] == customer_id]
            if not customer_row.empty:
                context['customer_segment'] = customer_row.iloc[0]['segment']
                context['industry'] = customer_row.iloc[0]['industry']
                context['region'] = customer_row.iloc[0]['region']
        
        # Set defaults if not found
        context.setdefault('product_family', 'Widgets')
        context.setdefault('cogs', 80.0)
        context.setdefault('customer_segment', 'Enterprise')
        context.setdefault('region', 'EMEA')
        context.setdefault('competitor_price', context['cogs'] * 1.3)
        
        return context
    
    def recommend_price(self, sku: str, customer_id: str, quantity: int,
                       country: str, channel: str, currency: str) -> Dict[str, Any]:
        """Generate comprehensive price recommendation using all agents"""
        
        # Step 1: Enrich context
        context = self._enrich_context(sku, customer_id, quantity, country, channel, currency)
        logger.info(f"Orchestrator processing recommendation for {sku} - {customer_id}")
        
        # Step 2: Get policy bounds from Rules Agent
        rules_result = self.rules_agent.execute(context)
        context.update(rules_result)
        
        # Step 3: Generate price candidates using elasticity optimization
        floor_price = rules_result['floor_price']
        ceiling_price = rules_result['ceiling_price']
        
        # Create price grid for optimization
        price_candidates = np.linspace(floor_price, ceiling_price, 20)
        
        # Step 4: Evaluate each price with WinRate and Elasticity agents
        candidate_scores = []
        for price in price_candidates:
            candidate_context = context.copy()
            candidate_context['proposed_price'] = price
            candidate_context['target_price'] = price
            
            # Get win probability
            winrate_result = self.winrate_agent.execute(candidate_context)
            
            # Get elasticity impact
            elasticity_result = self.elasticity_agent.execute(candidate_context)
            
            # Calculate expected value (simple scoring)
            margin = price - context['cogs']
            win_prob = winrate_result['win_probability']
            expected_margin = margin * win_prob
            
            candidate_scores.append({
                'price': price,
                'expected_margin': expected_margin,
                'win_probability': win_prob,
                'margin': margin,
                'elasticity_score': elasticity_result['revenue_change_pct']
            })
        
        # Step 5: Select optimal prices
        # Target: maximize expected margin
        target_candidate = max(candidate_scores, key=lambda x: x['expected_margin'])
        target_price = target_candidate['price']
        
        # Stretch: highest viable price (win_prob > 0.2)
        viable_candidates = [c for c in candidate_scores if c['win_probability'] > 0.2]
        stretch_price = max(viable_candidates, key=lambda x: x['price'])['price'] if viable_candidates else ceiling_price
        
        # Step 6: Get final metrics for target price
        final_context = context.copy()
        final_context.update({
            'target_price': target_price,
            'proposed_price': target_price,
            'floor_price': floor_price,
            'stretch_price': stretch_price
        })
        
        final_winrate = self.winrate_agent.execute(final_context)
        final_elasticity = self.elasticity_agent.execute(final_context)
        
        # Step 7: Generate explanation
        explanation_context = final_context.copy()
        explanation_context.update({
            'win_probability': final_winrate['win_probability'],
            'price_elasticity': final_elasticity['price_elasticity'],
            'approval_band': self.rules_agent.get_approval_band(target_price, context['cogs'], context)
        })
        
        explanation_result = self.explainer_agent.execute(explanation_context)
        
        # Step 8: Compile final recommendation
        result = {
            'floor': round(floor_price, 2),
            'target': round(target_price, 2),
            'stretch': round(stretch_price, 2),
            'p_win_at_target': final_winrate['win_probability'],
            'reasons': [
                explanation_result['explanation'],
                f"Expected margin optimization: ${target_candidate['expected_margin']:.2f}",
                f"Policy compliance: {explanation_context['approval_band']}"
            ],
            'agent_insights': {
                'rules': rules_result['reasons'],
                'winrate': final_winrate['reasons'],
                'elasticity': final_elasticity['reasons'],
                'explanation': explanation_result['key_insights']
            },
            'confidence_score': self._calculate_confidence(final_winrate, final_elasticity, rules_result)
        }
        
        logger.info(f"Recommendation complete: target=${target_price:.2f}, win_prob={final_winrate['win_probability']:.0%}")
        return result
    
    def score_price(self, sku: str, customer_id: str, quantity: int,
                   country: str, channel: str, currency: str, proposed_price: float) -> Dict[str, Any]:
        """Score a proposed price using all agents"""
        
        # Enrich context
        context = self._enrich_context(sku, customer_id, quantity, country, channel, currency)
        context['proposed_price'] = proposed_price
        
        # Get agent assessments
        rules_result = self.rules_agent.execute(context)
        winrate_result = self.winrate_agent.execute(context)
        elasticity_result = self.elasticity_agent.execute(context)
        
        # Calculate metrics
        cogs = context['cogs']
        expected_margin = (proposed_price - cogs) * winrate_result['win_probability']
        approval_band = self.rules_agent.get_approval_band(proposed_price, cogs, context)
        
        # Generate explanation
        explanation_context = context.copy()
        explanation_context.update({
            'win_probability': winrate_result['win_probability'],
            'price_elasticity': elasticity_result['price_elasticity'],
            'approval_band': approval_band,
            'expected_margin': expected_margin
        })
        
        explanation_result = self.explainer_agent.execute(explanation_context)
        
        result = {
            'p_win': winrate_result['win_probability'],
            'expected_margin': round(expected_margin, 2),
            'approval_band': approval_band,
            'reasons': [
                explanation_result['explanation'],
                f"ML win probability: {winrate_result['win_probability']:.0%}",
                f"Elasticity impact: {elasticity_result['demand_change_pct']:+.1%}"
            ],
            'agent_insights': {
                'rules': rules_result['reasons'],
                'winrate': winrate_result['reasons'],
                'elasticity': elasticity_result['reasons']
            }
        }
        
        return result
    
    def get_win_curve(self, sku: str, customer_id: str, quantity: int,
                     country: str, channel: str, currency: str) -> List[Dict[str, float]]:
        """Generate win probability curve using ML model"""
        
        context = self._enrich_context(sku, customer_id, quantity, country, channel, currency)
        rules_result = self.rules_agent.execute(context)
        
        # Create price range
        floor_price = rules_result['floor_price']
        ceiling_price = rules_result['ceiling_price']
        price_range = np.linspace(floor_price, ceiling_price, 15)
        
        # Get win curve from ML agent
        curve = self.winrate_agent.get_win_curve(context, price_range)
        
        return curve
    
    def _calculate_confidence(self, winrate_result: Dict, elasticity_result: Dict, rules_result: Dict) -> str:
        """Calculate overall confidence in recommendation"""
        confidence_factors = []
        
        # High win probability = confident
        if winrate_result['win_probability'] > 0.6:
            confidence_factors.append(1)
        elif winrate_result['win_probability'] > 0.4:
            confidence_factors.append(0.7)
        else:
            confidence_factors.append(0.3)
        
        # Stable elasticity = confident  
        elasticity = abs(elasticity_result['price_elasticity'])
        if elasticity < 2.0:
            confidence_factors.append(0.9)
        else:
            confidence_factors.append(0.5)
        
        # Policy compliance = confident
        if 'APPROVED' in str(rules_result.get('approval_bands', [])):
            confidence_factors.append(1.0)
        else:
            confidence_factors.append(0.6)
        
        avg_confidence = sum(confidence_factors) / len(confidence_factors)
        
        if avg_confidence > 0.8:
            return "High"
        elif avg_confidence > 0.6:
            return "Medium"
        else:
            return "Low"
