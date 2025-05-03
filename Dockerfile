FROM python:3.12-slim

# Install PostgreSQL client library and build tools
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/* \

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Make entrypoint script executable
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh


EXPOSE 8501 8000

ENTRYPOINT ["/entrypoint.sh"]
CMD ["sh", "-c", "streamlit run frontend/app.py & uvicorn frontend/main:app --host 0.0.0.0 --port 8000"]