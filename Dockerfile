FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

RUN git clone https://github.com/pewdiepie-archdaemon/odysseus.git . && \
    pip install --no-cache-dir -r requirements.txt

EXPOSE 10000

ENV PYTHONUNBUFFERED=1
ENV APP_BIND=0.0.0.0
ENV AUTH_ENABLED=true

CMD ["sh", "-c", "python -m uvicorn app:app --host 0.0.0.0 --port $PORT"]
