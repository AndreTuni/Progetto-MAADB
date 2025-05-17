import psycopg2
from psycopg2 import sql as psycopg2_sql
from psycopg2.extras import DictCursor
# from psycopg2.errors import UndefinedTable # Specific error for table not found

from fastapi import FastAPI, HTTPException, Path, Depends, Query  # Query is already here
from db.mongo_client import db
from db.neo4j_client import driver
from db.postgres_client import get_db_connection, close_postgres_pool
from pymongo.errors import ConnectionFailure
from typing import Dict, List, Any, Optional  # ADDED Optional
from neo4j.exceptions import ServiceUnavailable, ClientError

from models.query_1.post_model import PostResponse
from models.query_4.model import GroupDetail, MemberInfo
from typing import Dict, List, Any, Optional, Annotated # Ensure Annotated is imported
from typing import Dict, List, Any, Optional, Annotated
# Import the new model and function
from models.query_7.model import MostUsedTagsResponse, get_most_used_tags_by_city_interest

app = FastAPI(
    title="MAADB API",
    description="API for interacting with MAADB databases (using psycopg2).",
    version="1.0.0"
)


# --- Event handlers for application startup and shutdown ---
@app.on_event("startup")
async def startup_event():
    from db.postgres_client import postgres_pool as pg_pool_to_check
    if pg_pool_to_check is None:
        print("CRITICAL: PostgreSQL pool (psycopg2) was not initialized successfully on startup!")
    else:
        print("FastAPI application started. PostgreSQL pool (psycopg2) should be available.")


@app.on_event("shutdown")
def shutdown_event():
    close_postgres_pool()
    print("FastAPI application shutting down. PostgreSQL pool closed.")


@app.get("/")
async def root():
    return {"message": "Welcome to MAADB API. Visit /docs for documentation."}


# --- MongoDB Routes ---
@app.get("/mongo/health", tags=["MongoDB"])
async def check_mongodb_connection():
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
        print(f"Unexpected error in /mongo/health: {e}")
        raise HTTPException(status_code=500, detail=f"An unexpected error occurred during MongoDB health check.")


@app.get("/mongo/first5", tags=["MongoDB"])
async def get_first_5_objects() -> Dict[str, List[Dict]]:
    results = {}
    collections_to_query = ["person", "post", "comment", "forum"]
    for collection_name in collections_to_query:
        collection = db[collection_name]
        cursor = collection.find().limit(5)
        documents = []
        async for doc in cursor:
            doc["_id"] = str(doc["_id"])
            documents.append(doc)
        results[collection_name] = documents
    return results


# --- PostgreSQL Routes (using psycopg2) ---
@app.get("/postgres/health", tags=["PostgreSQL"])
def check_postgres_connection(pg_conn: psycopg2.extensions.connection = Depends(get_db_connection)):
    try:
        with pg_conn.cursor() as cursor:
            cursor.execute("SELECT version();")
            version_info = cursor.fetchone()
            pg_conn.commit()
            return {
                "status": "PostgreSQL connection is healthy",
                "server_info": version_info[0] if version_info else "N/A"
            }
    except psycopg2.Error as e:
        if pg_conn: pg_conn.rollback()
        raise HTTPException(status_code=500, detail=f"PostgreSQL (psycopg2) connection check failed: {e}")
    except Exception as e:
        if pg_conn: pg_conn.rollback()
        print(f"Unexpected error in /postgres/health (psycopg2): {e}")
        raise HTTPException(status_code=500,
                            detail="An unexpected error occurred during PostgreSQL health check (psycopg2).")


@app.get("/postgres/first5", tags=["PostgreSQL"])
def get_first_5_records_postgres(pg_conn: psycopg2.extensions.connection = Depends(get_db_connection)) -> Dict[
    str, List[Dict]]:
    results = {}
    tables_to_query = ["organization", "place", "tag", "tagclass"]
    try:
        for table_name in tables_to_query:
            try:
                query = psycopg2_sql.SQL("SELECT * FROM {} LIMIT 5").format(psycopg2_sql.Identifier(table_name))
                with pg_conn.cursor(cursor_factory=DictCursor) as cursor:
                    cursor.execute(query)
                    records = cursor.fetchall()
                    table_results = [dict(record) for record in records]
                    results[table_name] = table_results
            except psycopg2.errors.UndefinedTable:
                results[table_name] = [{"error": f"Table '{table_name}' not found."}]
            except psycopg2.Error as e:
                if pg_conn: pg_conn.rollback()
                results[table_name] = [{"error": f"Error querying table '{table_name}' (psycopg2): {str(e)}"}]
        pg_conn.commit()
        return results
    except Exception as e:
        if pg_conn: pg_conn.rollback()
        print(f"Unexpected error in /postgres/first5 (psycopg2): {e}")
        raise HTTPException(status_code=500, detail=f"Failed to fetch PostgreSQL records (psycopg2): {str(e)}")


# --- Neo4j Routes ---
@app.get("/neo4j/health", tags=["Neo4j"])
def check_neo4j_connection():
    try:
        with driver.session(database="neo4j") as session:
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
def get_first_5_relationships_neo4j() -> Dict[str, List[Dict[str, Any]]]:
    try:
        results = {}
        with driver.session(database="neo4j") as session:
            type_query = "CALL db.relationshipTypes() YIELD relationshipType RETURN collect(relationshipType) as types"
            types_result = session.run(type_query)
            relationship_types = types_result.single(strict=True)["types"] if types_result.peek() else []
            for rel_type in relationship_types:
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
        person_document = await db.person.find_one({"email": {"$in": [user_email]}})
        if not person_document:
            raise HTTPException(status_code=404, detail=f"Person with email '{user_email}' not found.")
        person_id_from_doc = person_document.get("id")
        if person_id_from_doc is None:
            raise HTTPException(status_code=500, detail="Person record exists but is missing the numeric 'id' field.")
        posts_cursor = db.post.find({"CreatorPersonId": person_id_from_doc})
        posts_list = [post_doc async for post_doc in posts_cursor]
        return posts_list
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in get_posts_by_user_email for {user_email}: {type(e).__name__} - {str(e)}")
        raise HTTPException(status_code=500, detail=f"An internal error occurred while fetching posts: {str(e)}")


# --- Helper function for Neo4j results (no changes) ---
def get_neo4j_results(tx, query, params):
    result = tx.run(query, params)
    return [record.data() for record in result]


# --- New Endpoint using PostgreSQL Pool (psycopg2) ---
@app.get(
    "/groups/by-work-and-forum/{target_year}",
    response_model=List[GroupDetail],
    summary="Find groups of people by shared company (since year) and forum",
    tags=["Complex Queries"]
)
async def find_groups_by_work_and_forum(
        target_year: int = Path(..., description="Target year (e.g., people working since this year or earlier).",
                                ge=1900, le=2100),
        limit: Optional[int] = Query(100, description="Maximum number of groups to return.", ge=1, le=100000),
        # ADDED limit parameter
        pg_conn: psycopg2.extensions.connection = Depends(get_db_connection)
):
    print(f"DEBUG: Entered find_groups_by_work_and_forum for target_year: {target_year}, limit: {limit}")
    # Using the two-stage query that worked well without indexes
    cypher_query = """
    MATCH (person:Person)-[workRel:WORK_AT]->(company:Company),
          (person)-[:MEMBER_OF]->(forum:Forum)
    WHERE workRel.workFrom IS NOT NULL AND workRel.workFrom <= $targetYear 
    WITH company, forum, count(person) AS groupSizeCalc 
    WHERE groupSizeCalc > 1

    MATCH (p:Person)-[w:WORK_AT]->(company), 
          (p)-[:MEMBER_OF]->(forum)
    WHERE w.workFrom IS NOT NULL AND w.workFrom <= $targetYear 
    WITH company, forum, collect(p.id) AS personMongoIds // Removed groupSizeCalc from here as it's not strictly needed for RETURN
    ORDER BY company.id, forum.id // For stable pagination with LIMIT
    RETURN company.id AS companyPsqlId,
           forum.id AS forumMongoId,
           personMongoIds
    LIMIT $limitParam // ADDED LIMIT clause
    """
    neo4j_params = {"targetYear": target_year, "limitParam": limit}  # ADDED limitParam to params
    groups_data = []

    try:
        print("DEBUG: Attempting Neo4j query...")
        with driver.session(database="neo4j") as session:
            raw_groups = session.read_transaction(get_neo4j_results, cypher_query, neo4j_params)
        print(f"DEBUG: Neo4j query returned {len(raw_groups)} raw groups.")  # Simplified log for potentially large list
        if len(raw_groups) > 0 and len(raw_groups) < 10:  # Log sample if small
            print(f"DEBUG: Sample raw_groups: {raw_groups[:3]}")

        if not raw_groups:
            print("DEBUG: No raw groups found from Neo4j. Committing PG and returning empty list.")
            pg_conn.commit()
            return []

        print(f"DEBUG: Processing {len(raw_groups)} groups...")
        for i, group_info in enumerate(raw_groups):
            # print(f"DEBUG: Processing group {i+1}/{len(raw_groups)}: {group_info}") # Can be verbose
            company_psql_id = group_info["companyPsqlId"]
            forum_mongo_id = group_info["forumMongoId"]
            person_mongo_ids = group_info["personMongoIds"]

            # print(f"DEBUG: Group {i+1} - CompanyPSQLID: {company_psql_id}, ForumMongoID: {forum_mongo_id}, PersonMongoIDs count: {len(person_mongo_ids)}")

            if not person_mongo_ids:
                # print(f"DEBUG: Group {i+1} - Skipping due to no personMongoIds.")
                continue

            company_name = "Unknown Company"
            try:
                # print(f"DEBUG: Group {i+1} - Querying PostgreSQL for company ID: {company_psql_id}")
                with pg_conn.cursor(cursor_factory=DictCursor) as cursor:
                    cursor.execute("SELECT name FROM organization WHERE id = %s", (company_psql_id,))
                    company_result = cursor.fetchone()
                if company_result:
                    company_name = company_result["name"]
                    # print(f"DEBUG: Group {i+1} - Found company name: '{company_name}'")
                else:
                    print(f"Warning: Group {i + 1} - Company with ID {company_psql_id} not found in PostgreSQL.")
            except psycopg2.Error as e:
                print(f"ERROR: Group {i + 1} - PostgreSQL error fetching company ID {company_psql_id} (psycopg2): {e}")
                pg_conn.rollback()

            forum_title = "Unknown Forum"
            # print(f"DEBUG: Group {i+1} - Querying MongoDB for forum ID: {forum_mongo_id}")
            forum_doc = await db.forum.find_one({"id": forum_mongo_id}, {"title": 1})
            if forum_doc:
                forum_title = forum_doc.get("title", "Unknown Forum")
                # print(f"DEBUG: Group {i+1} - Found forum title: '{forum_title}'")
            else:
                print(f"Warning: Group {i + 1} - Forum with ID {forum_mongo_id} not found in MongoDB.")

            member_details_list = []
            # print(f"DEBUG: Group {i+1} - Querying MongoDB for {len(person_mongo_ids)} person details...")
            persons_cursor = db.person.find(
                {"id": {"$in": person_mongo_ids}},
                {"id": 1, "firstName": 1, "lastName": 1, "email": 1, "_id": 0}
            )
            async for person_doc in persons_cursor:
                member_details_list.append(MemberInfo(**person_doc))
            # print(f"DEBUG: Group {i+1} - Found {len(member_details_list)} member details from MongoDB.")

            if member_details_list:
                groups_data.append(
                    GroupDetail(
                        companyId=company_psql_id,
                        companyName=company_name,
                        forumId=forum_mongo_id,
                        forumTitle=forum_title,
                        members=member_details_list,
                    )
                )
                # print(f"DEBUG: Group {i+1} - Added to final groups_data.")
            # else:
            # print(f"DEBUG: Group {i+1} - No member details found, group not added (Person IDs: {person_mongo_ids}).")

        print("DEBUG: All groups processed. Committing PG.")
        pg_conn.commit()

    except ServiceUnavailable as e:
        print(f"ERROR: Neo4j service unavailable: {e}")
        if pg_conn: pg_conn.rollback()
        raise HTTPException(status_code=503, detail=f"Neo4j service unavailable: {e}")
    except ClientError as e:
        print(f"ERROR: Neo4j client error: {e}")
        if pg_conn: pg_conn.rollback()
        raise HTTPException(status_code=500, detail=f"Neo4j client error: {e}")
    except ConnectionFailure as e:
        print(f"ERROR: MongoDB connection error: {e}")
        if pg_conn: pg_conn.rollback()
        raise HTTPException(status_code=503, detail=f"MongoDB connection error: {e}")
    except psycopg2.Error as e:
        print(f"ERROR: PostgreSQL (psycopg2) database error: {e}")
        if pg_conn: pg_conn.rollback()
        raise HTTPException(status_code=500, detail=f"PostgreSQL (psycopg2) database error: {e}")
    except Exception as e:
        print(
            f"ERROR: An unexpected error occurred in find_groups_by_work_and_forum (psycopg2): {type(e).__name__} - {str(e)}")
        if pg_conn: pg_conn.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred (psycopg2): {str(e)}")

    print(f"DEBUG: Returning {len(groups_data)} groups from endpoint.")
    return groups_data


# --- Endpoint for Query 7: Most Used Tags by City Interest ---
@app.get(
    "/tags/most-used-by-city-interest/{user_email}",
    response_model=MostUsedTagsResponse,
    summary="Find most used tags (by interest) for users in the same city as the given user",
    tags=["Complex Queries", "Tags"]
)
async def get_tags_by_city_interest(
        user_email: Annotated[str, Path(description="Email address of the user to find city from.")],
        # CHANGED EmailStr to str
        top_n: Annotated[int, Query(description="Number of top tags to return.", ge=1, le=100)] = 10,
        pg_conn: psycopg2.extensions.connection = Depends(get_db_connection)
):
    try:
        result = await get_most_used_tags_by_city_interest(
            user_email=user_email,  # user_email is now a simple str
            top_n=top_n,
            mongo_db_async=db,
            neo4j_driver_sync=driver,
            pg_conn_sync=pg_conn
        )

        if not result.tags and result.message:
            if "User with email" in result.message and "not found" in result.message:
                raise HTTPException(status_code=404, detail=result.message)
        return result

    except HTTPException:
        raise
    except psycopg2.Error as e:
        print(f"ERROR: PostgreSQL (psycopg2) unhandled database error in endpoint: {e}")
        if pg_conn: pg_conn.rollback()
        raise HTTPException(status_code=500, detail=f"PostgreSQL (psycopg2) database error: {str(e)}")
    except Exception as e:
        print(f"Unexpected error in /tags/most-used-by-city-interest for {user_email}: {type(e).__name__} - {str(e)}")
        if pg_conn: pg_conn.rollback()
        raise HTTPException(status_code=500, detail=f"An unexpected server error occurred: {str(e)}")