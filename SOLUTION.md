# 🚀 Itaú Personalization Service

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=for-the-badge&logo=fastapi)
![Pandas](https://img.shields.io/badge/Pandas-150458?style=for-the-badge&logo=pandas&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-2496ED?style=for-the-badge&logo=docker&logoColor=white)

> **Missão:** Entregar um microserviço de recomendações personalizadas focado em **latência ultrabaixa**, **observabilidade** e **resiliência** em produção, atuando como a ponte entre o modelo de Machine Learning e o App do banco.

---

## ⚙️ 1. Como Executar (Ambiente Imutável)

A aplicação foi conteinerizada para garantir consistência entre os ambientes de desenvolvimento e produção.

### 🐳 Via Docker (Padrão Ouro)
```bash
docker build -t ita-personalization-service .
docker run -p 8000:8000 ita-personalization-service