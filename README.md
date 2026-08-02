# Personalization Service

![Python](https://img.shields.io/badge/Python-3.14-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.141.1-green)
![Scikit-Learn](https://img.shields.io/badge/Scikit--Learn-ML-orange)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED)
![Prometheus](https://img.shields.io/badge/Prometheus-Observability-E6522C)
![License](https://img.shields.io/badge/License-MIT-lightgrey)

Microsserviço de recomendação de produtos desenvolvido em **FastAPI** e **Machine Learning (Scikit-Learn)**, projetado com foco em **baixa latência**, carregamento otimizado em memória, isolamento do ciclo de vida da aplicação utilizando **lifespan**, tratamento robusto de **Cold Start** e observabilidade pronta para ambientes corporativos.

> **Objetivo:** Demonstrar a implementação de um motor de recomendação com foco em desempenho, escalabilidade e boas práticas de Engenharia de Software, utilizando FastAPI, Machine Learning e observabilidade.

---

# 🏗️ 1. Arquitetura do Sistema

O microsserviço realiza o carregamento da base de produtos, eventos e do modelo de Machine Learning durante o **startup** da aplicação.

Essa estratégia elimina leituras síncronas de disco durante as requisições, mantendo os dados em memória RAM e proporcionando **baixa latência durante a inferência**.

### Fluxo da aplicação

<img width="1833" height="600" alt="estrutura1" src="https://github.com/user-attachments/assets/3b01275d-80a3-4349-96e7-948ada8732f7" />

---

<img width="331" height="198" alt="image" src="https://github.com/user-attachments/assets/f7834ae3-34db-4c7f-914e-7cdee32bface" />

---

<img width="566" height="418" alt="image" src="https://github.com/user-attachments/assets/013b920c-9924-4a6a-b981-f4036bcc06f9" />

---

<img width="418" height="348" alt="image" src="https://github.com/user-attachments/assets/40e9774b-97aa-4b72-bc6f-5a49578f1989" />

---

<img width="639" height="359" alt="image" src="https://github.com/user-attachments/assets/df868c60-b1a9-41b3-9129-fedd122ac40a" />

---

<img width="648" height="455" alt="image" src="https://github.com/user-attachments/assets/abc39954-fe14-4d2e-9197-30c554576843" />

```bash
Recomendações geradas por Cold Start (Popularidade):
[{'product_id': 'p_030', 'score': 0.801}, {'product_id': 'p_000', 'score': 0.652}, {'product_id': 'p_005', 'score': 0.543}, {'product_id': 'p_040', 'score': 0.541}, {'product_id': 'p_011', 'score': 0.485}]
```
<img width="461" height="199" alt="image" src="https://github.com/user-attachments/assets/35516fae-a388-4725-852b-4b9d32d75e2d" />

---

# ⚡ 2. Principais Funcionalidades

## ✅ Warm Start Inteligente

Usuários já conhecidos são processados por um pipeline de Machine Learning composto por:

- StandardScaler
- LogisticRegression

O modelo calcula o **Propensity Score**, estimando a probabilidade de conversão para cada produto.

---

## ✅ Tratamento de Cold Start

Quando o usuário não possui histórico suficiente:

- o sistema identifica automaticamente a ausência de dados;
- evita falhas na inferência;
- utiliza um ranking baseado na popularidade global dos produtos.

Essa estratégia garante disponibilidade da API mesmo para novos usuários.

---

## ✅ Feature Store em Memória

Durante o startup, os eventos são cruzados com o catálogo de produtos utilizando Pandas.

A partir desse processamento é criada uma Feature Store residente em memória contendo informações como:

- categorias preferidas;
- afinidade do usuário;
- frequência de interação;
- `user_affinity_match`.

Como todas essas informações permanecem carregadas em RAM, as consultas evitam acesso ao disco durante a inferência.

---

## ✅ Observabilidade

A aplicação já nasce preparada para produção.

### Logs estruturados

Utilizando **Structlog**, todas as requisições possuem logs em formato JSON contendo:

- timestamp;
- endpoint;
- método HTTP;
- latência;
- status code;
- metadados da requisição.

---

### Métricas

As métricas são expostas no padrão **OpenMetrics**, compatível com Prometheus.

Exemplos:

- quantidade de requisições;
- latência;
- throughput;
- disponibilidade.

```text
GET /metrics
```

---

# 🛠️ 3. Tecnologias Utilizadas

| Categoria | Tecnologia |
|------------|------------|
| Linguagem | Python 3.10+ / 3.14 |
| Framework | FastAPI |
| Servidor ASGI | Uvicorn |
| Machine Learning | Scikit-Learn |
| Manipulação de Dados | Pandas |
| Modelo | LogisticRegression |
| Pré-processamento | StandardScaler |
| Observabilidade | Prometheus Client |
| Logging | Structlog |
| Testes | Pytest + TestClient |
| Testes de Carga | Locust |
| Containerização | Docker |

---

# 📂 4. Estrutura do Projeto

```text
ITA-PERSONALIZATION-SERVICE/
│
├── src/
│   └── ita_personalization_service/
│       │
│       ├── data/
│       │   ├── events.csv
│       │   └── products.csv
│       │
│       ├── model/
│       │   ├── model.pkl
│       │   └── model_card.json
│       │
│       └── main.py
│
├── tests/
│   └── test_main.py
│
├── locustfile.py
├── Dockerfile
├── pyproject.toml
├── README.md
└── .gitignore
```

---

# ⚙️ 5. Como Executar o Projeto

Você pode executar o projeto de duas formas: utilizando **Docker** (recomendado para um ambiente isolado e reproduzível) ou **localmente** utilizando Python.

---

## 🐳 Opção A — Executando com Docker (Recomendado)

### Build da imagem

```bash
docker build -t itau-personalization .
```

### Execute o container

```bash
docker run -p 8000:8000 itau-personalization
```

Após iniciar o container:

| Serviço | URL |
|---------|-----|
| API | http://127.0.0.1:8000 |
| Swagger | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |

---

## 💻 Opção B — Executando Localmente

### Clone o repositório

```bash
git clone https://github.com/MatheusHFrancisco/itau-personalization-case.git
cd ITA-PERSONALIZATION-SERVICE
```

### Crie o ambiente virtual

```bash
python -m venv .venv
```

Windows

```bash
.venv\Scripts\activate
```

Linux / macOS

```bash
source .venv/bin/activate
```

### Instale as dependências

Como o projeto utiliza **pyproject.toml**, execute:

```bash
pip install -e .
```

### Execute a aplicação

```bash
uvicorn src.ita_personalization_service.main:app --reload
```
ou
```bash
python -m uvicorn src.ita_personalization_service.main:app --reload
```
---

## 🌐 Endpoints Disponíveis

| Serviço | URL |
|---------|-----|
| API | http://127.0.0.1:8000 |
| Health | http://127.0.0.1:8000/health |
| Swagger | http://127.0.0.1:8000/docs |
| ReDoc | http://127.0.0.1:8000/redoc |
| Metrics | http://127.0.0.1:8000/metrics |

---

# 🔌 6. Endpoints

## GET /health

Verifica se a aplicação está operacional.

```json
{
  "status": "healthy"
}
```

---

## GET /recommendations/{user_id}

Retorna recomendações para um usuário.

### Query Parameters

| Nome | Tipo | Padrão |
|------|------|---------|
| top_k | int | 5 |

### Exemplo

```text
GET /recommendations/u_0231?top_k=5
```

### Resposta

```json
{
  "user_id": "u_0231",
  "cold_start": false,
  "recommendations": [
    {
      "product_id": "p_089",
      "score": 0.8421
    },
    {
      "product_id": "p_041",
      "score": 0.8014
    }
  ]
}
```

---

## GET /metrics

Endpoint utilizado pelo Prometheus para coleta das métricas da aplicação.

---

# 🧪 7. Executando os Testes

Executar todos os testes:

```bash
python -m pytest -v
```

Executar com cobertura:

```bash
python -m pytest --cov=src --cov-report=term-missing
```

---

# 📈 8. Performance

A arquitetura foi desenhada para minimizar latência e suportar **múltiplas requisições simultâneas**.

<img width="1488" height="442" alt="image" src="https://github.com/user-attachments/assets/177f78b7-b3bc-4d06-876e-e20a1aae639e" />

Características implementadas:

- carregamento único do modelo durante o startup;
- Feature Store residente em memória;
- ausência de leitura síncrona durante a inferência;
- reutilização do modelo entre requisições;
- arquitetura stateless;
- compatível com múltiplos workers do Uvicorn/Gunicorn.

---

# 🔬 Validação de Performance (Locust)

Para validar a capacidade da API sob concorrência, foi utilizado o **Locust**, simulando múltiplos usuários realizando chamadas simultâneas ao endpoint de recomendações.

O objetivo dos testes foi validar:

- comportamento sob alta concorrência;
- estabilidade da aplicação;
- latência durante Warm Start;
- comportamento em cenários de Cold Start;
- impacto do carregamento em memória.

Executar o teste:

```bash
locust -f locustfile.py
```

---

# 🚀 9. Roadmap de Evolução

<img width="1600" height="688" alt="image" src="https://github.com/user-attachments/assets/8d70f998-a2a2-4c39-8ed7-3b0b09c8bc8a" />

Em um ambiente corporativo com milhões de acessos simultâneos, a arquitetura pode evoluir para:

## Mensageria

- Apache Kafka

---

## Feature Store Distribuída

- Redis Cluster
- 
---

## Infraestrutura

- Docker
- Kubernetes
- Horizontal Pod Autoscaler (HPA)

---

## Observabilidade

- Prometheus
- Grafana
- OpenTelemetry

---

## MLOps

- MLflow
- CI/CD para modelos

---

# 📈 10. Observabilidade: Estado Atual vs. Visão de Evolução

Em ambientes corporativos de missão crítica, a observabilidade não se resume apenas a "saber se a API está no ar", mas sim a entender a saúde profunda do negócio e do modelo de Machine Learning em tempo real.

## 🔍 O que logamos e medimos atualmente (MVP)

O microsserviço já conta com instrumentação nativa cobrindo os pilares fundamentais de engenharia de software:
* **Logs Estruturados (JSON via `structlog`):** Cada requisição gera rastros limpos contendo timestamp, método HTTP, endpoint acessado, status code e a latência exata da inferência.
* **Métricas de Performance no Padrão OpenMetrics (`/metrics`):** Exposição pronta para raspagem por ferramentas de monitoramento, cobrindo contadores de requisições, throughput e disponibilidade.
* **Isolamento de Erros por Flag:** Registro explícito nos metadados da resposta indicando se a requisição utilizou o modelo de Machine Learning (`cold_start: false`) ou o fallback de popularidade (`cold_start: true`).

---

## 🚀 O que adicionaríamos com mais tempo e escala

Caso este microsserviço fosse integrado ao ecossistema de uma grande instituição com milhões de acessos simultâneos, a estratégia de observabilidade evoluiria para:

* Tracing Distribuído (OpenTelemetry)
  * *O que faria:* Mapearia o ciclo de vida completo de ponta a ponta. Se uma recomendação falhasse ou demorasse, conseguiríamos rastrear exatamente onde o tempo foi gasto (ex: se o gargalo ocorreu na serialização do JSON, no cálculo do *propensity score* do Scikit-Learn ou na busca em cache).
* **Alertas Inteligentes (Prometheus + Alertmanager):**
  * *O que faria:* Criação de regras de disparo automático para situações críticas, como:
    * Taxa de erro HTTP 5xx acima de 1% em uma janela de 5 minutos.
    * Latência de p99 estourando o SLA estabelecido (ex: > 100ms).
* **Dashboards Executivos de MLOps (Grafana):**
  * *O que faria:* Painéis consolidados em tempo real cruzando métricas técnicas com métricas de negócio (ex: taxa de conversão dos produtos recomendados, proporção exata de usuários atendidos por *Warm Start* vs *Cold Start* e uso da Feature Store).
