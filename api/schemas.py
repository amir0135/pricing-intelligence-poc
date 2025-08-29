from pydantic import BaseModel, Field
from typing import List, Optional

class RecommendIn(BaseModel):
    sku: str
    customer_id: str
    quantity: int
    country: str
    channel: str
    currency: str

class RecommendOut(BaseModel):
    floor: float
    target: float
    stretch: float
    p_win_at_target: float
    reasons: List[str]

class ScoreIn(BaseModel):
    sku: str
    customer_id: str
    quantity: int
    country: str
    channel: str
    currency: str
    proposed_price: float

class ScoreOut(BaseModel):
    p_win: float
    expected_margin: float
    approval_band: str
    reasons: List[str]

class CurvePoint(BaseModel):
    price: float
    p_win: float

class CurveOut(BaseModel):
    curve: List[CurvePoint]
