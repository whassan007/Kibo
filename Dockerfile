FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY kibo-is/requirements.txt /app/kibo-is/requirements.txt
RUN pip install --no-cache-dir -r /app/kibo-is/requirements.txt \
    langgraph \
    langgraph-checkpoint-sqlite \
    reportlab \
    python-docx \
    pyyaml \
    mcp \
    pydantic-settings

RUN groupadd --system kibo && useradd --system --uid 10001 --gid kibo kibo

COPY . /app
RUN chown -R kibo:kibo /app

WORKDIR /app/kibo-is
EXPOSE 8000

HEALTHCHECK --interval=15s --timeout=5s --retries=3 \
  CMD curl -f http://localhost:8000/api/system/health || exit 1

USER kibo

CMD ["uvicorn", "agent_gateway:app", "--host", "0.0.0.0", "--port", "8000"]
