import psycopg
from fastapi import FastAPI
from db.mongo_client import db
from db.neo4j_client import driver, get_friends_of
from db.postgres_client import conn
from fastapi import APIRouter, HTTPException
from pymongo.errors import ConnectionFailure
from fastapi import FastAPI, HTTPException
from pymongo import MongoClient
from typing import Dict, List

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

# 🔍 Basic MongoDB query

@app.get("/mongo/person/{name}")
async def get_person_by_name(name: str):
    cursor = db.people.find({"firstName": name})
    results = []
    async for doc in cursor:
        doc["_id"] = str(doc["_id"])  # Convert ObjectId to string
        results.append(doc)

    if not results:
        raise HTTPException(status_code=404, detail="No person found")

    return results


# 🔍 Basic Neo4j query
@app.get("/neo4j/friends/{name}")
async def get_friends(name: str):
    friends = get_friends_of(name)
    return {"friends": friends}

# 🔀 Cross-database query
@app.get("/cross/{name}")
async def cross_query(name: str):
    person = await db.people.find_one({"name": name})
    friends = get_friends_of(name)
    return {
        "person": {
            "name": name,
            "email": person["email"] if person else None
        },
        "friends": friends
    }
@app.get("/mongo/health")
async def check_mongodb_connection():
    """
    Checks the connection to the MongoDB database.
    Returns a success message if the connection is healthy.
    Raises an HTTPException with a 500 status code if the connection fails.
    """
    try:
        # Use the hello command (available since MongoDB 3.6)
        result = await db.command("hello")
        if result and result.get("ok") == 1:
            return {"status": "MongoDB connection is healthy", "server_info": result.get("me", "N/A")}
        else:
             raise HTTPException(status_code=500, detail="MongoDB connection check failed: 'hello' command did not return ok:1")
    except ConnectionFailure as e:
        raise HTTPException(status_code=500, detail=f"MongoDB connection check failed: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")

@app.get("/mongo/first5")
async def get_first_5_objects() -> Dict[str, List[Dict]]:
    """
    Retrieves the first 5 objects from the 'person', 'post', 'comment', and 'forum'
    collections in the MongoDB database.

    Returns:
        A dictionary where the keys are the collection names and the values are
        lists of the first 5 documents in each collection.  If a collection
        does not exist, it will return an empty list for that collection.
    """
    results = {}
    collections = ["person", "post", "comment", "forum"]

    for collection_name in collections:
        collection = db[collection_name]  # Get the collection object
        cursor = collection.find().limit(5)  # Find first 5 documents
        documents = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])  # Convert ObjectId to string for JSON serialization
            documents.append(doc)
        results[collection_name] = documents
    return results


@app.get("/postgres/health")
def check_postgres_connection():
    """
    Checks the connection to the PostgreSQL database.
    Returns a success message if the connection is healthy.
    Raises an HTTPException with a 500 status code if the connection fails.
    """
    try:
        # Execute a simple query to verify the connection
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
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred: {e}")


@app.get("/postgres/first5")
def get_first_5_records() -> Dict[str, List[Dict]]:
    """
    Retrieves the first 5 records from the 'organization', 'place', 'tag', and 'tagclass'
    tables in the PostgreSQL database.

    Returns:
        A dictionary where the keys are the table names and the values are
        lists of the first 5 records in each table. If a table does not exist,
        it will return an empty list for that table.
    """
    results = {}
    tables = ["organization", "place", "tag", "tagclass"]

    try:
        for table_name in tables:
            try:
                # Query to get first 5 rows
                query = f"SELECT * FROM {table_name} LIMIT 5"

                with conn.cursor(row_factory=psycopg.rows.dict_row) as cursor:
                    cursor.execute(query)
                    records = cursor.fetchall()

                    # Handle any non-JSON serializable values
                    table_results = []
                    for record in records:
                        # Convert any non-serializable types to strings
                        for key, value in record.items():
                            if not isinstance(value, (str, int, float, bool, type(None), list, dict)):
                                record[key] = str(value)
                        table_results.append(record)

                    results[table_name] = table_results
            except psycopg.errors.UndefinedTable:
                # Handle case where table doesn't exist
                results[table_name] = []
            except Exception as e:
                # Handle other errors for this specific table
                results[table_name] = [{"error": str(e)}]

        return results
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch records: {e}")