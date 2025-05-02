import psycopg2
from config import settings

conn = psycopg2.connect(
    dbname=settings.postgres_db,
    user=settings.postgres_user,
    password=settings.postgres_password,
    host=settings.postgres_host,
    port=settings.postgres_port
)
