from locust import HttpUser, task, between
import random

class ItauPersonalizationUser(HttpUser):
    # Simula o "think time" do usuário humano no app (entre 1 e 3 segundos)
    wait_time = between(1, 3)

    @task(1)
    def health_check(self):
        """Testa o pulso da aplicação"""
        self.client.get("/health", name="01_Health_Check")

    @task(6)
    def warm_start_recommendation(self):
        """Simula a massa de clientes ativos buscando recomendações"""
        # Simulando um cliente conhecido (que passará pelo modelo scikit-learn)
        self.client.get("/recommendations/u_0231", name="02_Warm_Start_Predict")

    @task(3)
    def cold_start_recommendation(self):
        """Simula a entrada de clientes novos no banco"""
        # Gera IDs aleatórios para sempre cair na trava do Cold Start
        novo_id = f"u_novo_{random.randint(1000, 9999)}"
        self.client.get(f"/recommendations/{novo_id}", name="03_Cold_Start_Fallback")