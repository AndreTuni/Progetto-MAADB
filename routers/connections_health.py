from fastapi import APIRouter, HTTPException, Depends

import psycopg2
from psycopg2.extras import DictCursor

from pymongo.errors import ConnectionFailure
from neo4j.exceptions import ServiceUnavailable, ClientError

from db.mongo_client import db
from db.neo4j_client import driver
from db.postgres_client import get_db_connection


router = APIRouter()


# --- MongoDB Health ---
@router.get("/mongo/health", tags=["MongoDB"])
async def check_mongodb_connection():
    """
    Checks the connection to the MongoDB database.
    Returns a success message if the connection is healthy.
    Raises an HTTPException with a 500 status code if the connection fails.
    """
    try:
        result = await db.command("hello")
        if result and result.get("ok") == 1:
            return {"status": "MongoDB connection is healthy", "server_info": result.get("me", "N/A")}
        else:
            raise HTTPException(status_code=500,
                                detail="MongoDB connection check failed: 'hello' command did not return ok:1")
    except ConnectionFailure as e:
        raise HTTPException(status_code=500, detail=f"MongoDB connection check failed: {e}")
    except Exception as e:
        # Log the exception for more details on the server side
        print(f"Unexpected error in /mongo/health: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during MongoDB health check.")
    

# --- PostgreSQL Health (using psycopg2) ---
@router.get("/postgres/health", tags=["PostgreSQL"])
def check_postgres_connection(pg_conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    """
    Checks the connection to the PostgreSQL database.
    """
    try:
        with pg_conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            return {
                "status": "PostgreSQL connection is healthy",
                "server_info": version
            }
    except psycopg2.Error as e:
        raise HTTPException(status_code=500, detail=f"PostgreSQL connection check failed: {e}")
    except Exception as e:
        print(f"Unexpected error in /postgres/health: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during PostgreSQL health check.")


# --- Neo4j Health ---
@router.get("/neo4j/health", tags=["Neo4j"])
def check_neo4j_connection():
    """
    Checks the connection to the Neo4j database.
    """
    try:
        with driver.session(database="neo4j") as session:  # Specify database if not default
            result = session.run("CALL dbms.components() YIELD name, versions, edition")
            record = result.single()
            if record:
                return {
                    "status": "Neo4j connection is healthy",
                    "server_info": {
                        "name": record["name"],
                        "version": record["versions"][0] if record["versions"] else "N/A",
                        "edition": record["edition"]
                    }
                }
            else:
                raise HTTPException(status_code=500,
                                    detail="Neo4j connection check failed: No data returned from dbms.components()")
    except ServiceUnavailable as e:
        raise HTTPException(status_code=500, detail=f"Neo4j connection check failed: Service unavailable - {e}")
    except ClientError as e:
        raise HTTPException(status_code=500, detail=f"Neo4j connection check failed: Client error - {e}")
    except Exception as e:
        print(f"Unexpected error in /neo4j/health: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during Neo4j health check.")