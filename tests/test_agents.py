import pytest
import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from api.model_service import recommend, score, curve
from agents.orchestrator import AgentOrchestrator

class TestAgentOrchestrator:
    """Test the multi-agent pricing system"""
    
    def setup_method(self):
        """Setup test environment"""
        self.orchestrator = AgentOrchestrator()
    
    def test_recommend_price(self):
        """Test price recommendation"""
        result = self.orchestrator.recommend_price(
            sku="SKU-001",
            customer_id="C-100", 
            quantity=10,
            country="DE",
            channel="Direct",
            currency="EUR"
        )
        
        assert "floor" in result
        assert "target" in result  
        assert "stretch" in result
        assert "p_win_at_target" in result
        assert "reasons" in result
        assert "confidence_score" in result
        
        # Check reasonable values
        assert result["floor"] < result["target"] < result["stretch"]
        assert 0 <= result["p_win_at_target"] <= 1
        assert result["confidence_score"] in ["High", "Medium", "Low"]
    
    def test_score_price(self):
        """Test price scoring"""
        result = self.orchestrator.score_price(
            sku="SKU-001",
            customer_id="C-100",
            quantity=10,
            country="DE", 
            channel="Direct",
            currency="EUR",
            proposed_price=120.0
        )
        
        assert "p_win" in result
        assert "expected_margin" in result
        assert "approval_band" in result
        assert "reasons" in result
        
        assert 0 <= result["p_win"] <= 1
        assert result["approval_band"] in ["APPROVED", "REVIEW", "REJECT"]
    
    def test_win_curve(self):
        """Test win probability curve"""
        result = self.orchestrator.get_win_curve(
            sku="SKU-001",
            customer_id="C-100", 
            quantity=10,
            country="DE",
            channel="Direct",
            currency="EUR"
        )
        
        assert len(result) > 0
        assert all("price" in point and "p_win" in point for point in result)
        
        # Check curve is reasonable (higher prices = lower win prob)
        prices = [point["price"] for point in result]
        win_probs = [point["p_win"] for point in result]
        
        assert prices == sorted(prices)  # Prices should be ascending
        
    def test_agent_insights(self):
        """Test that agent insights are provided"""
        result = self.orchestrator.recommend_price(
            sku="SKU-001", 
            customer_id="C-100",
            quantity=10,
            country="DE",
            channel="Direct", 
            currency="EUR"
        )
        
        assert "agent_insights" in result
        insights = result["agent_insights"]
        
        assert "rules" in insights
        assert "winrate" in insights
        assert "elasticity" in insights
        assert "explanation" in insights

class TestAPICompatibility:
    """Test backward compatibility with existing API"""
    
    def test_recommend_function(self):
        """Test recommend function"""
        result = recommend(
            sku="SKU-001",
            customer_id="C-100",
            quantity=10, 
            country="DE",
            channel="Direct",
            currency="EUR"
        )
        
        assert "floor" in result
        assert "target" in result
        assert "stretch" in result
        assert "p_win_at_target" in result
        assert "reasons" in result
    
    def test_score_function(self):
        """Test score function"""
        result = score(
            sku="SKU-001",
            customer_id="C-100",
            quantity=10,
            country="DE", 
            channel="Direct",
            currency="EUR",
            proposed_price=120.0
        )
        
        assert "p_win" in result
        assert "expected_margin" in result
        assert "approval_band" in result
        assert "reasons" in result
    
    def test_curve_function(self):
        """Test curve function"""
        result = curve(
            sku="SKU-001",
            customer_id="C-100",
            quantity=10,
            country="DE",
            channel="Direct", 
            currency="EUR"
        )
        
        assert len(result) > 0
        assert all("price" in point and "p_win" in point for point in result)

class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_invalid_sku(self):
        """Test with invalid SKU"""
        orchestrator = AgentOrchestrator()
        
        result = orchestrator.recommend_price(
            sku="INVALID-SKU",
            customer_id="C-100", 
            quantity=10,
            country="DE",
            channel="Direct",
            currency="EUR"
        )
        
        # Should still work with defaults
        assert "floor" in result
        assert "target" in result
    
    def test_edge_quantities(self):
        """Test with edge case quantities"""
        orchestrator = AgentOrchestrator()
        
        # Very small quantity
        result1 = orchestrator.recommend_price(
            sku="SKU-001",
            customer_id="C-100",
            quantity=1,
            country="DE", 
            channel="Direct",
            currency="EUR"
        )
        
        # Very large quantity  
        result2 = orchestrator.recommend_price(
            sku="SKU-001",
            customer_id="C-100",
            quantity=100,
            country="DE",
            channel="Direct", 
            currency="EUR"
        )
        
        assert result1["target"] != result2["target"]  # Should be different

if __name__ == "__main__":
    pytest.main([__file__, "-v"])
