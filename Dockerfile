FROM python:3.12-slim

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