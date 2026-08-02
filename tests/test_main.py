from fastapi.testclient import TestClient
from src.ita_personalization_service.main import app, FeatureStore

def test_health_check():
    """
    Valida se o endpoint de saúde da aplicação está respondendo corretamente,
    garantindo que o Uvicorn subiu sem erros fatais.
    """
    with TestClient(app) as client:
        # Act
        response = client.get("/health")
        
        # Assert
        assert response.status_code == 200
        assert response.json()["status"] == "ok"


def test_warm_start_recommendation():
    """
    Garante que usuários conhecidos (com histórico na Feature Store)
    recebam recomendações ranqueadas pelo modelo de ML (Cold Start = False).
    """
    with TestClient(app) as client:
        response = client.get("/recommendations/u_0231")
        data = response.json()
        
        assert response.status_code == 200
        assert data["user_id"] == "u_0231"
        assert data["cold_start"] is False
        assert len(data["recommendations"]) == 5
        assert isinstance(data["recommendations"][0]["score"], float)


def test_cold_start_recommendation():
    """
    Garante que usuários novos ou sem histórico não causem erro 500,
    recebendo automaticamente o fallback de popularidade global (Cold Start = True).
    """
    with TestClient(app) as client:
        response = client.get("/recommendations/u_9999_novo")
        data = response.json()
        
        assert response.status_code == 200
        assert data["user_id"] == "u_9999_novo"
        assert data["cold_start"] is True
        assert len(data["recommendations"]) == 5


def test_unit_feature_store_build():
    """
    Valida a construção em memória da Feature Store durante o startup da aplicação,
    garantindo que as tabelas de cruzamento contenham todas as features do modelo.
    """
    # Arrange & Act
    store = FeatureStore()
    store.build()
    
    # Assert
    assert store.user_features is not None
    assert store.products_df is not None
    
    colunas_esperadas = [
        "user_id", "product_id", "interactions", 
        "price", "avg_rating", "popularity_score", "user_affinity_match"
    ]
    colunas_reais = list(store.user_features.columns)
    
    assert all(col in colunas_reais for col in colunas_esperadas)
    assert not store.user_features.empty


def test_top_k_parameter_modification():
    """
    Valida se a API respeita o limite de paginação dinâmico (top_k) passado via query params.
    """
    with TestClient(app) as client:
        response = client.get("/recommendations/u_0231?top_k=2")
        data = response.json()
        
        assert response.status_code == 200
        assert len(data["recommendations"]) == 2


def test_metrics_endpoint_is_exposed():
    """
    Garante que as métricas do Prometheus estão sendo exportadas no formato OpenMetrics.
    """
    with TestClient(app) as client:
        response = client.get("/metrics")
        
        assert response.status_code == 200
        assert "http_requests_total" in response.text