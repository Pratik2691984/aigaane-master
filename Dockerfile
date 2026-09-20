FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    AIGAANE_ENABLE_CANONICAL_DHATU_WRITE=0 \
    PORT=8080

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir httpx -r requirements.txt

COPY . .

EXPOSE 8080
CMD ["uvicorn", "api.index:app", "--host", "0.0.0.0", "--port", "8080"]