import time
import pickle
from pathlib import Path
from contextlib import asynccontextmanager

import pandas as pd
import structlog
from fastapi import FastAPI, HTTPException
import json

logger = structlog.get_logger()

BASE_DIR = Path(__file__).resolve().parent
DATA_EVENTS_PATH = BASE_DIR / "data" / "events.csv"
DATA_PRODUCTS_PATH = BASE_DIR / "data" / "products.csv"
MODEL_PATH = BASE_DIR / "model" / "model.pkl"


class FeatureStore:
    def __init__(self):
        self.user_features = None
        self.products_df = None
        self.user_top_category_map = {}

    def build(self):
        start_time = time.time()
        logger.info("Iniciando construcao da Feature Store...")

        events = pd.read_csv(DATA_EVENTS_PATH)
        products = pd.read_csv(DATA_PRODUCTS_PATH)

        self.products_df = products.copy()

        interactions = (
            events.groupby(["user_id", "product_id"])
            .size()
            .reset_index(name="interactions")
        )
        
        events_with_cat = events.merge(
            products[["product_id", "category"]], on="product_id", how="left"
        )

        user_top_category_df = (
            events_with_cat.groupby(["user_id", "category"])
            .size()
            .reset_index(name="cat_count")
            .sort_values(
                ["user_id", "cat_count", "category"], ascending=[True, False, True]
            )
            .drop_duplicates(subset=["user_id"], keep="first")
            .rename(columns={"category": "top_category"})
        )
        
        self.user_top_category_map = user_top_category_df.set_index("user_id")["top_category"].to_dict()

        df_features = interactions.merge(products, on="product_id", how="left")
        df_features = df_features.merge(
            user_top_category_df[["user_id", "top_category"]], on="user_id", how="left"
        )
        df_features["user_affinity_match"] = (
            df_features["category"] == df_features["top_category"]
        ).astype(int)

        colunas_finais = [
            "user_id",
            "product_id",
            "interactions",
            "price",
            "avg_rating",
            "popularity_score",
            "user_affinity_match",
        ]

        self.user_features = df_features[colunas_finais].copy()
        logger.info(
            "Feature Store pronta.",
            tempo_ms=round((time.time() - start_time) * 1000, 2),
        )


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
        logger.info(
            "Modelo carregado.", tempo_ms=round((time.time() - start_time) * 1000, 2)
        )


store = FeatureStore()
ml_service = ModelService()


@asynccontextmanager
async def lifespan(app: FastAPI):
    store.build()
    ml_service.load()
    yield


app = FastAPI(title="Personalization Service", lifespan=lifespan)

from prometheus_fastapi_instrumentator import Instrumentator

instrumentator = Instrumentator().instrument(app)
instrumentator.expose(app)


@app.get("/health")
def health_check():
    return {"status": "ok", "timestamp": time.time()}


@app.get("/recommendations/{user_id}")
def get_recommendations(user_id: str, top_k: int = 5):
    start_time = time.time()
    
    top_cat = store.user_top_category_map.get(user_id)
    
    if not top_cat:
        logger.info("cold_start_triggered", user_id=user_id)
        top_popular = store.products_df.nlargest(top_k, "popularity_score")
        
        recs = top_popular[["product_id", "popularity_score"]].rename(
            columns={"popularity_score": "score"}
        ).to_dict(orient="records")
        
        latency = (time.time() - start_time) * 1000
        logger.info("request_finished", user_id=user_id, latency_ms=round(latency, 2), cold_start=True)
        
        return {
            "user_id": user_id, 
            "recommendations": recs, 
            "cold_start": True, # Garantido pelo fluxo do 'if'
            "metadata": {
                "model_version": "fallback_popularity",
                "latency_ms": round(latency, 2)
            }
        }
    
    candidates = store.products_df.copy()
    candidates["user_affinity_match"] = (candidates["category"] == top_cat).astype(int)
    
    user_history = store.user_features[store.user_features["user_id"] == user_id]
    candidates = candidates.merge(
        user_history[["product_id", "interactions"]], 
        on="product_id", 
        how="left"
    ).fillna({"interactions": 0})
    
    X = candidates[ml_service.feature_cols]
    X_scaled = ml_service.scaler.transform(X)
    
    candidates["score"] = ml_service.model.predict_proba(X_scaled)[:, 1]
    top_preds = candidates.nlargest(top_k, "score")
    
    recs = top_preds[["product_id", "score"]].to_dict(orient="records")
    
    latency = (time.time() - start_time) * 1000
    logger.info("request_finished", user_id=user_id, latency_ms=round(latency, 2), cold_start=False)
    
    return {
        "user_id": user_id, 
        "recommendations": recs, 
        "cold_start": False,
        "metadata": {
            "model_version": ml_service.model.__class__.__name__, # Extrai o nome real do modelo do Pickle
            "latency_ms": round(latency, 2)
        }
    }

@app.get("/model/info")
def get_model_info():
    try:
        with open(BASE_DIR / "model" / "model_card.json", "r") as f:
            model_card = json.load(f)
        return {
            "status": "loaded",
            "model_name": model_card.get("model_name"),
            "version": model_card.get("version"),
            "input_features": ml_service.feature_cols
        }
    except Exception as e:
        logger.error("model_card_not_found", error=str(e))
        return {"status": "loaded", "features": ml_service.feature_cols}

@app.get("/debug/features/{user_id}")
def debug_user_features(user_id: str):
    top_cat = store.user_top_category_map.get(user_id)
    
    if not top_cat:
        return {"user_id": user_id, "status": "no_history", "cold_start": True}
        
    user_history = store.user_features[store.user_features["user_id"] == user_id]
    
    return {
        "user_id": user_id,
        "cold_start": False,
        "top_category_affinity": top_cat,
        "total_interactions_recorded": len(user_history),
        "interacted_products": user_history[["product_id", "interactions"]].to_dict(orient="records")
    }