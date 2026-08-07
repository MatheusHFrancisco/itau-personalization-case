FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml .

RUN uv pip install --system -r pyproject.toml

COPY src/ ./src/
COPY data/ ./data/
COPY model/ ./model/

EXPOSE 8000

CMD ["python", "-m", "uvicorn", "src.ita_personalization_service.main:app", "--host", "0.0.0.0", "--port", "8000"]