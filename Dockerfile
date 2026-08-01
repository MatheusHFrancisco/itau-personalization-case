# TOP 1 ABSOLUTO MUNDIAL: Imagem oficial enxuta para máxima performance
FROM python:3.12-slim

# Variáveis de ambiente para o Python não criar arquivos desnecessários
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

# Instala o gerenciador de pacotes ultrarrápido (uv)
RUN pip install --no-cache-dir uv

# Copia os arquivos de dependência primeiro (para usar o cache do Docker)
COPY pyproject.toml .

# Instala as dependências no sistema do container
RUN uv pip install --system -r pyproject.toml

# Copia o núcleo da nossa aplicação, modelos e dados
COPY src/ ./src/
COPY data/ ./data/
COPY model/ ./model/

# Expõe a porta que o FastAPI vai rodar
EXPOSE 8000

# Comando imutável de inicialização do servidor em produção
CMD ["python", "-m", "uvicorn", "src.ita_personalization_service.main:app", "--host", "0.0.0.0", "--port", "8000"]