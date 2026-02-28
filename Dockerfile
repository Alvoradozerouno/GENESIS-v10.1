FROM python:3.12-slim

LABEL maintainer="GENESIS Engine v10.1"
LABEL description="EU Regulatory Compliance API — Basel III, DORA, GDPR, AI Act, MiFID II, AML6, PSD2, Solvency II, EBA"

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    GENESIS_API_KEY=changeme-in-production \
    LLAMA_BASE=http://llama:8090

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

COPY requirements.txt ./
RUN uv pip install --system -r requirements.txt

COPY genesis_api.py ./
COPY ui/ ui/

RUN mkdir -p data

EXPOSE 8080

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD curl -sf http://localhost:8080/api/health || exit 1

CMD ["uvicorn", "genesis_api:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "2"]
