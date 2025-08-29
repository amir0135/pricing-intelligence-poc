from .base_agent import BaseAgent
from typing import Dict, Any
import pandas as pd
from pathlib import Path
import json

class RulesAgent(BaseAgent):
    """Agent that applies business policy rules for pricing bounds"""
    
    def __init__(self):
        super().__init__("RulesAgent")
        self.policy_df = self._load_policy()
        
    def _load_policy(self) -> pd.DataFrame:
        """Load policy rules from CSV"""
        data_dir = Path(__file__).parent.parent / "data" / "sample_csv"
        policy_path = data_dir / "policy.csv"
        if policy_path.exists():
            return pd.read_csv(policy_path)
        return pd.DataFrame()
    
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Apply business rules to determine price bounds and approval bands"""
        sku = context.get('sku')
        region = context.get('region', 'EMEA')
        product_family = context.get('product_family', 'Widgets')
        cogs = context.get('cogs', 100.0)
        
        # Find applicable policy
        policy_row = self.policy_df[
            (self.policy_df['region'] == region) & 
            (self.policy_df['family'] == product_family)
        ]
        
        if policy_row.empty:
            # Default fallback policy
            min_margin_pct = 0.10
            ceiling_pct = 2.0
            approval_bands = ["APPROVED", "REVIEW", "REJECT"]
        else:
            policy = policy_row.iloc[0]
            min_margin_pct = policy['min_margin_pct']
            ceiling_pct = policy['ceiling_pct']
            try:
                approval_bands = json.loads(policy['approval_bands_json'])['bands']
            except:
                approval_bands = ["APPROVED", "REVIEW", "REJECT"]
        
        floor_price = cogs * (1 + min_margin_pct)
        ceiling_price = cogs * ceiling_pct
        
        result = {
            'floor_price': round(floor_price, 2),
            'ceiling_price': round(ceiling_price, 2),
            'min_margin_pct': min_margin_pct,
            'approval_bands': approval_bands,
            'policy_source': f"{region}-{product_family}",
            'reasons': [f"Policy floor: {min_margin_pct*100:.1f}% margin", 
                       f"Policy ceiling: {ceiling_pct}x COGS"]
        }
        
        self.log_execution(context, result)
        return result
    
    def get_approval_band(self, proposed_price: float, cogs: float, context: Dict[str, Any]) -> str:
        """Determine approval band for a proposed price"""
        rules_result = self.execute(context)
        margin_pct = (proposed_price - cogs) / cogs if cogs > 0 else 0
        
        if margin_pct >= rules_result['min_margin_pct']:
            if proposed_price <= rules_result['ceiling_price']:
                return "APPROVED"
            else:
                return "REVIEW"  # Above ceiling
        else:
            return "REJECT"  # Below minimum margin
