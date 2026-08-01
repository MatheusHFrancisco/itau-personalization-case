# Personalization Service - Solução Arquitetural

Este repositório contém a implementação do microserviço de recomendações personalizadas, focado em baixa latência, observabilidade e resiliência em produção.

## 1. Como Executar o Projeto

A aplicação foi conteinerizada para garantir a imutabilidade do ambiente de produção.

**Opção A: Via Docker (Recomendado)**
```bash
# 1. Construir a imagem
docker build -t ita-personalization-service .

# 2. Rodar o container na porta 8000
docker run -p 8000:8000 ita-personalization-service