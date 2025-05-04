FROM python:3.12-slim


## Disable Transparent Huge Pages
#RUN echo never | tee /sys/kernel/mm/transparent_hugepage/enabled
#RUN echo never | tee /sys/kernel/mm/transparent_hugepage/defrag

# Install procps (contains sysctl) if not already present
#RUN apt-get update && apt-get install -y procps
#
## Add the sysctl setting to a config file (this file itself doesn't apply the setting)
#RUN echo "vm.max_map_count = 1677720" >> /etc/sysctl.d/99-mongodb.conf


## Apply the sysctl settings
#RUN sysctl -p /etc/sysctl.d/99-mongodb.conf
#


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