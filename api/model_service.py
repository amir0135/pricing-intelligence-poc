import pandas as pd
import numpy as np
from typing import Dict, Any, List
from loguru import logger
from pathlib import Path
import sys

# Add agents to path
sys.path.append(str(Path(__file__).parent.parent))
from agents.orchestrator import AgentOrchestrator

# Initialize the agent orchestrator
orchestrator = AgentOrchestrator()

# Legacy functions for backward compatibility
data_dir = Path(__file__).parent.parent / "data" / "sample_csv"

def load_csv(name: str) -> pd.DataFrame:
    path = data_dir / f"{name}.csv"
    if path.exists():
        return pd.read_csv(path)
    return pd.DataFrame()

products = load_csv("products")
customers = load_csv("customers")
orders = load_csv("orders")
cogs = load_csv("cogs")
policy = load_csv("policy")

def get_policy(region: str, family: str) -> Dict[str, Any]:
    row = policy[(policy['region'] == region) & (policy['family'] == family)]
    if not row.empty:
        return row.iloc[0].to_dict()
    return {"min_margin_pct": 0.1, "ceiling_pct": 2.0, "approval_bands_json": '{}'}

def get_cogs(product_id: str) -> float:
    row = cogs[cogs['product_id'] == product_id]
    if not row.empty:
        return float(row.iloc[0]['cogs'])
    return 10.0

# --- Enhanced functions using agent orchestrator ---
def recommend(sku: str, customer_id: str, quantity: int, country: str, channel: str, currency: str) -> Dict[str, Any]:
    """Generate price recommendation using multi-agent system"""
    try:
        logger.info(f"Generating recommendation for {sku} - {customer_id}")
        result = orchestrator.recommend_price(sku, customer_id, quantity, country, channel, currency)
        return result
    except Exception as e:
        logger.error(f"Error in recommend: {e}")
        return {"error": str(e)}

def score(sku: str, customer_id: str, quantity: int, country: str, channel: str, currency: str, proposed_price: float) -> Dict[str, Any]:
    """Score a proposed price using multi-agent system"""
    try:
        logger.info(f"Scoring price {proposed_price} for {sku} - {customer_id}")
        result = orchestrator.score_price(sku, customer_id, quantity, country, channel, currency, proposed_price)
        return result
    except Exception as e:
        logger.error(f"Error in score: {e}")
        return {"error": str(e)}

def curve(sku: str, customer_id: str, quantity: int, country: str, channel: str, currency: str) -> List[Dict[str, float]]:
    """Generate win probability curve using multi-agent system"""
    try:
        logger.info(f"Generating curve for {sku} - {customer_id}")
        result = orchestrator.get_win_curve(sku, customer_id, quantity, country, channel, currency)
        return result
    except Exception as e:
        logger.error(f"Error in curve: {e}")
        return []

# Legacy win_prob function for backward compatibility
def win_prob(price: float, base: float, channel: str, region: str) -> float:
    adj = 0.0
    if channel.lower() == "direct":
        adj += 0.2
    if region.upper() in ["DE", "EMEA"]:
        adj += 0.1
    p = 1 / (1 + np.exp((price - base) / (0.2 * base)))
    return max(0.01, min(0.99, p + adj))
