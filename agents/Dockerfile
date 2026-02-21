FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    libportaudio2 portaudio19-dev gcc && \
    rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY agents/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY agents/ ./agents/
COPY data/ ./data/
ENTRYPOINT ["python", "agents/verdict_session.py"]
