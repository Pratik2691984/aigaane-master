FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /app

# Copy the requirements from the backend folder
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
RUN python -c "import vidyut; vidyut.download_data('/app/data/vidyut')"

# Copy the backend code and the data
COPY backend/ /app/
COPY backend/data/ /app/data/

EXPOSE 8080
# Run the new main.py in the backend folder
CMD exec uvicorn main:app --host 0.0.0.0 --port $PORT
