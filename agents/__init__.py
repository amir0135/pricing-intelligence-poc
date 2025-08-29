from abc import ABC, abstractmethod
from typing import Dict, Any, List
from loguru import logger

class BaseAgent(ABC):
    """Base agent interface for pricing intelligence components"""
    
    def __init__(self, name: str):
        self.name = name
        
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent logic and return results"""
        pass
    
    def log_execution(self, context: Dict[str, Any], result: Dict[str, Any]):
        """Log agent execution for transparency"""
        logger.info(f"Agent {self.name} executed with context keys: {list(context.keys())}")
        logger.debug(f"Agent {self.name} result: {result}")
