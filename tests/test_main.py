from fastapi.testclient import TestClient
from src.ita_personalization_service.main import app
from src.ita_personalization_service.main import FeatureStore

def test_health_check():
    with TestClient(app) as client:
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "ok"

def test_warm_start_recommendation():
    with TestClient(app) as client:
        response = client.get("/recommendations/u_0231")
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == "u_0231"
        assert data["cold_start"] is False
        assert len(data["recommendations"]) == 5
        assert isinstance(data["recommendations"][0]["score"], float)

def test_cold_start_recommendation():
    with TestClient(app) as client:
        response = client.get("/recommendations/u_9999_novo")
        assert response.status_code == 200
        
        data = response.json()
        assert data["user_id"] == "u_9999_novo"
        assert data["cold_start"] is True
        assert len(data["recommendations"]) == 5

def test_unit_feature_store_build():
    store = FeatureStore()
    store.build()
    
    assert store.user_features is not None
    assert store.products_df is not None
    
    colunas_esperadas = ["user_id", "product_id", "interactions", "price", "avg_rating", "popularity_score", "user_affinity_match"]
    colunas_reais = list(store.user_features.columns)
    
    assert all(col in colunas_reais for col in colunas_esperadas)
    assert not store.user_features.empty