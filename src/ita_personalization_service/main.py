import time
import pickle
from pathlib import Path
from contextlib import asynccontextmanager

import pandas as pd
import structlog
from fastapi import FastAPI, HTTPException

logger = structlog.get_logger()

BASE_DIR = Path(__file__).resolve().parent
DATA_EVENTS_PATH = BASE_DIR / "data" / "events.csv"
DATA_PRODUCTS_PATH = BASE_DIR / "data" / "products.csv"
MODEL_PATH = BASE_DIR / "model" / "model.pkl"

class FeatureStore:
    def __init__(self):
        self.user_features = None
        self.products_df = None

    def build(self):
        start_time = time.time()
        logger.info("Iniciando construcao da Feature Store...")

        events = pd.read_csv(DATA_EVENTS_PATH)
        products = pd.read_csv(DATA_PRODUCTS_PATH)
        
        self.products_df = products.copy()

        interactions = events.groupby(["user_id", "product_id"]).size().reset_index(name="interactions")
        events_with_cat = events.merge(products[["product_id", "category"]], on="product_id", how="left")
        
        user_top_category = (
            events_with_cat.groupby(["user_id", "category"])
            .size()
            .reset_index(name="cat_count")
            .sort_values(["user_id", "cat_count"], ascending=[True, False])
            .drop_duplicates(subset=["user_id"], keep="first")
            .rename(columns={"category": "top_category"})
        )

        df_features = interactions.merge(products, on="product_id", how="left")
        df_features = df_features.merge(user_top_category[["user_id", "top_category"]], on="user_id", how="left")
        df_features["user_affinity_match"] = (df_features["category"] == df_features["top_category"]).astype(int)

        colunas_finais = [
            "user_id", "product_id", "interactions", 
            "price", "avg_rating", "popularity_score", "user_affinity_match"
        ]
        
        self.user_features = df_features[colunas_finais].copy()
        logger.info("Feature Store pronta.", tempo_ms=round((time.time() - start_time)*1000, 2))

class ModelService:
    def __init__(self):
        self.model = None
        self.scaler = None
        self.feature_cols = None

    def load(self):
        start_time = time.time()
        logger.info("Carregando artefatos do modelo...")
        with open(MODEL_PATH, "rb") as f:
            artifact = pickle.load(f)
        
        self.model = artifact["model"]
        self.scaler = artifact["scaler"]
        self.feature_cols = artifact["feature_cols"]
        logger.info("Modelo carregado.", tempo_ms=round((time.time() - start_time)*1000, 2))

store = FeatureStore()
ml_service = ModelService()

@asynccontextmanager
async def lifespan(app: FastAPI):
    store.build()
    ml_service.load()
    yield

app = FastAPI(title="Personalization Service", lifespan=lifespan)

from prometheus_fastapi_instrumentator import Instrumentator

app = FastAPI(title="Personalization Service", lifespan=lifespan)

instrumentator = Instrumentator().instrument(app)
instrumentator.expose(app)

@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": time.time()}

@app.get("/recommendations/{user_id}")
def get_recommendations(user_id: str, top_k: int = 5):
    start_time = time.time()
    
    user_data = store.user_features[store.user_features["user_id"] == user_id]
    
    if user_data.empty:
        logger.info("cold_start_triggered", user_id=user_id)
        
        top_popular = store.products_df.sort_values("popularity_score", ascending=False).head(top_k)
        
        recs = [{"product_id": str(row.name if "product_id" not in row else row["product_id"]), "score": float(row["popularity_score"])} for _, row in top_popular.iterrows()]
        
        latency = (time.time() - start_time) * 1000
        logger.info("request_finished", user_id=user_id, latency_ms=round(latency, 2), cold_start=True)
        return {"user_id": user_id, "recommendations": recs, "cold_start": True}
    
    X = user_data[ml_service.feature_cols]
    
    X_scaled = ml_service.scaler.transform(X)
    scores = ml_service.model.predict_proba(X_scaled)[:, 1]
    
    user_data = user_data.copy()
    user_data["score"] = scores
    top_preds = user_data.sort_values("score", ascending=False).head(top_k)
    
    recs = [{"product_id": str(row["product_id"]), "score": float(row["score"])} for _, row in top_preds.iterrows()]
    
    latency = (time.time() - start_time) * 1000
    logger.info("request_finished", user_id=user_id, latency_ms=round(latency, 2), cold_start=False)
    
    return {"user_id": user_id, "recommendations": recs, "cold_start": False}