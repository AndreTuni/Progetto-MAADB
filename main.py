import psycopg
from fastapi import FastAPI, HTTPException, Path  # Added Path
from db.mongo_client import db
from db.neo4j_client import driver
from db.postgres_client import conn  # Assuming conn is your psycopg connection pool or similar
from pymongo.errors import ConnectionFailure
from typing import Dict, List, Any  # Added List
from neo4j.exceptions import ServiceUnavailable, ClientError

# Assuming PostResponse is defined in models.post_models
# Create models/post_models.py if it doesn't exist
# from models.post_models import PostResponse
# For now, as a placeholder if the file is missing, let's define a minimal one
# THIS IS A PLACEHOLDER - REPLACE WITH YOUR ACTUAL MODEL IMPORT
from pydantic import BaseModel


class PostResponse(BaseModel):  # Placeholder
    id: int
    content: str | None = None
    creationDate: str
    CreatorPersonId: int
    # Add other fields as per your actual PostResponse model


app = FastAPI(
    title="MAADB API",
    description="API for interacting with MAADB databases.",
    version="1.0.0"
)


@app.get("/")
async def root():
    return {"message": "Welcome to MAADB API. Visit /docs for documentation."}


@app.get("/mongo/health", tags=["MongoDB"])
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


@app.get("/mongo/first5", tags=["MongoDB"])
async def get_first_5_objects() -> Dict[str, List[Dict]]:
    """
    Retrieves the first 5 objects from the 'person', 'post', 'comment', and 'forum'
    collections in the MongoDB database.
    """
    results = {}
    collections_to_query = ["person", "post", "comment", "forum"]

    for collection_name in collections_to_query:
        collection = db[collection_name]
        cursor = collection.find().limit(5)
        documents = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
            documents.append(doc)
        results[collection_name] = documents
    return results


@app.get("/postgres/health", tags=["PostgreSQL"])
def check_postgres_connection():
    """
    Checks the connection to the PostgreSQL database.
    """
    try:
        with conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            version = cursor.fetchone()[0]
            return {
                "status": "PostgreSQL connection is healthy",
                "server_info": version
            }
    except psycopg.Error as e:
        raise HTTPException(status_code=500, detail=f"PostgreSQL connection check failed: {e}")
    except Exception as e:
        print(f"Unexpected error in /postgres/health: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during PostgreSQL health check.")


@app.get("/postgres/first5", tags=["PostgreSQL"])
def get_first_5_records_postgres() -> Dict[str, List[Dict]]:  # Renamed to avoid conflict if used elsewhere
    """
    Retrieves the first 5 records from specified PostgreSQL tables.
    """
    results = {}
    tables_to_query = ["organization", "place", "tag", "tagclass"]  # Ensure these tables exist

    try:
        for table_name in tables_to_query:
            try:
                query = f"SELECT * FROM {psycopg.sql.Identifier(table_name).as_string(conn)} LIMIT 5"  # Secure table name
                with conn.cursor(row_factory=psycopg.rows.dict_row) as cursor:
                    cursor.execute(query)
                    records = cursor.fetchall()
                    table_results = []
                    for record in records:
                        # Basic serialization for common non-JSON types (e.g., datetime, decimal)
                        serialized_record = {}
                        for key, value in record.items():
                            if hasattr(value, 'isoformat'):  # For datetime, date
                                serialized_record[key] = value.isoformat()
                            # Add other type conversions if necessary (e.g., Decimal to str)
                            else:
                                serialized_record[key] = value
                        table_results.append(serialized_record)
                    results[table_name] = table_results
            except psycopg.errors.UndefinedTable:
                results[table_name] = [{"error": f"Table '{table_name}' not found."}]
            except Exception as e:
                results[table_name] = [{"error": f"Error querying table '{table_name}': {str(e)}"}]
        return results
    except Exception as e:
        print(f"Unexpected error in /postgres/first5: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch PostgreSQL records: {str(e)}")


@app.get("/neo4j/health", tags=["Neo4j"])
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


@app.get("/neo4j/first5", tags=["Neo4j"])
def get_first_5_relationships_neo4j() -> Dict[str, List[Dict[str, Any]]]:  # Renamed
    """
    Retrieves the first 5 relationships for each type from the Neo4j database.
    """
    try:
        results = {}
        with driver.session(database="neo4j") as session:
            type_query = "CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) as types"
            types_result = session.run(type_query)
            relationship_types = types_result.single(strict=True)["types"] if types_result.peek() else []

            for rel_type in relationship_types:
                # Use parameters to avoid injection with relationship type if it could be user-influenced
                # For now, assuming rel_type from db.relationshipTypes() is safe.
                query = f"""
                MATCH (s)-[r:`{rel_type}`]->(t)
                RETURN s.id AS source_id, elementId(s) AS source_elementId, labels(s) AS source_labels, properties(s) as source_props,
                       elementId(r) AS rel_elementId, properties(r) as rel_props,
                       t.id AS target_id, elementId(t) AS target_elementId, labels(t) AS target_labels, properties(t) as target_props
                LIMIT 5
                """
                rel_results = session.run(query)
                relationship_list = [dict(record) for record in rel_results]
                results[rel_type] = relationship_list
            return results
    except ServiceUnavailable as e:
        raise HTTPException(status_code=500, detail=f"Neo4j service unavailable: {e}")
    except Exception as e:
        print(f"Unexpected error in /neo4j/first5: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch Neo4j relationships: {str(e)}")


# --- Endpoint for finding posts by user email ---
@app.get("/by-email/{user_email}",
            response_model=List[PostResponse],
            summary="Find all posts created by a person given one of their emails",
            tags=["Posts"])
async def get_posts_by_user_email(
        user_email: str = Path(..., description="An email address of the post creator.", example="Jan16@hotmail.com")
):
    try:
        # If email is an array field in MongoDB
        person_document = await db.person.find_one({"email": {"$in": [user_email]}})

        if not person_document:
            raise HTTPException(status_code=404, detail=f"Person with email '{user_email}' not found.")

        person_id = person_document.get("id") or str(person_document.get("_id"))
        if not person_id:
            raise HTTPException(status_code=500, detail=f"Person record exists but is missing an 'id'.")

        posts_cursor = db.post.find({"CreatorPersonId": person_id})
        posts_list = []

        async for post in posts_cursor:
            post["_id"] = str(post["_id"])  # Required if PostResponse doesn't handle ObjectId
            posts_list.append(post)

        return posts_list

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

