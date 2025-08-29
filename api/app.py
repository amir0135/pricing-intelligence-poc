from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from .schemas import RecommendIn, RecommendOut, ScoreIn, ScoreOut, CurveOut, CurvePoint
from . import model_service
from typing import List

app = FastAPI(title="Pricing Intelligence API")

origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost:5173",
    "http://localhost",
    "http://127.0.0.1",
    "powerbi://api.powerbi.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/api/recommend", response_model=RecommendOut)
def recommend(payload: RecommendIn):
    logger.info(f"Recommend request: {payload}")
    result = model_service.recommend(**payload.dict())
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.post("/api/score", response_model=ScoreOut)
def score(payload: ScoreIn):
    logger.info(f"Score request: {payload}")
    result = model_service.score(**payload.dict())
    if "error" in result:
        raise HTTPException(status_code=400, detail=result["error"])
    return result

@app.get("/api/curve", response_model=CurveOut)
def get_curve(sku: str, customer_id: str, quantity: int, country: str, channel: str, currency: str):
    logger.info(f"Curve request: sku={sku}, customer_id={customer_id}")
    curve = model_service.curve(sku, customer_id, quantity, country, channel, currency)
    return {"curve": curve}

@app.post("/api/feedback")
def feedback(request: Request):
    payload = request.json()
    logger.info(f"Feedback: {payload}")
    return {"status": "received"}
