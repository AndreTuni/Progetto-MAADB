import psycopg2
from psycopg2 import pool
from config import settings


# Connection parameters for psycopg2
DB_ARGS = {
    "dbname": settings.postgres_db,
    "user": settings.postgres_user,
    "password": settings.postgres_password,
    "host": settings.postgres_host,
    "port": settings.postgres_port
}

try:
    postgres_pool = psycopg2.pool.SimpleConnectionPool(minconn=1, maxconn=10, **DB_ARGS)
except psycopg2.OperationalError as e:
    print(f"CRITICAL: Failed to initialize PostgreSQL connection pool (psycopg2): {e}")
    postgres_pool = None

# This is now a generator function suitable for FastAPI's "dependency with yield"
def get_db_connection():
    """
    FastAPI dependency that provides a PostgreSQL connection from the pool (psycopg2).
    Ensures the connection is returned to the pool when the request is done.
    """
    if postgres_pool is None:
        # This error will propagate and FastAPI will return a 500 error.
        raise Exception("PostgreSQL connection pool (psycopg2) is not available or not initialized.")

    conn = None
    try:
        conn = postgres_pool.getconn()
        yield conn # The actual connection object is yielded here
    except psycopg2.Error as e:
        # If getting the connection fails,conn might be None or partially initialized.
        # This exception will be caught by FastAPI's error handling.
        print(f"Error getting connection from pool: {e}")
        raise # Re-raise the psycopg2 error
    finally:
        if conn:
            # This block executes after the request is processed or if an error occurred
            # in the 'try' block of the route handler (if not caught before yielding)
            try:
                postgres_pool.putconn(conn)
            except psycopg2.Error as e:
                print(f"Error putting connection back to pool: {e}")


# Function to close the pool on application shutdown
def close_postgres_pool():
    if postgres_pool:
        postgres_pool.closeall()
        print("PostgreSQL connection pool (psycopg2) closed.")