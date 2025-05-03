import psycopg
from config import settings

conn = psycopg.connect(
    dbname=settings.postgres_db,
    user=settings.postgres_user,
    password=settings.postgres_password,
    host=settings.postgres_host,
    port=settings.postgres_port
)