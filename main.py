import psycopg
from fastapi import FastAPI, HTTPException, Path
from pydantic import BaseModel  # Added Path
from db.mongo_client import db
from db.neo4j_client import driver
from db.postgres_client import conn  # Assuming conn is your psycopg connection pool or similar
from pymongo.errors import ConnectionFailure
from typing import Dict, List, Any, Optional  # Added List
from neo4j.exceptions import ServiceUnavailable, ClientError
from models.post_model import ForumResponse,SecondDegreeCommentResponse, TagResponse


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


@app.get("/forumsEmail/{user_email}",
 response_model=List[ForumResponse],
            summary="Find all forums a person belongs to, given their email",
            tags=["Forum"])
async def get_forums_by_user_email(
        user_email: str = Path(..., description="An email address of the forum member.", example="Jan16@hotmail.com")
):
    try:
        # If email is an array field in MongoDB
        person_document = await db.person.find_one({"email": {"$in": [user_email]}})

        if not person_document:
            raise HTTPException(status_code=404, detail=f"Person with email '{user_email}' not found.")

        person_id = person_document.get("id") or str(person_document.get("_id"))
        if not person_id:
            raise HTTPException(status_code=500, detail=f"Person record exists but is missing an 'id'.")

        # Found membership user-forums
        with driver.session(database="neo4j") as session:
            query = """
            MATCH (p:Person {id: $person_id})-[r:MEMBER_OF]->(f:Forum)
            RETURN f.id AS forum_id,
            r.creationDate AS membership_creation_date
            """
            neo4j_results = list(session.run(query, person_id=person_id))
        
        if not neo4j_results:
            raise HTTPException(status_code=404, detail=f"No forum memberships found for person ID {person_id}.")

        # Recover the forums
        forum_ids = [record["forum_id"] for record in neo4j_results]
        forum_docs = await db.forum.find({"id": {"$in": forum_ids}}).to_list(length=None)

        # Mappa {forum_id: creation_date}
        membership_dates = {
            record["forum_id"]: record["membership_creation_date"]
            for record in neo4j_results
        }

        # 🔁 Conta i membri per ciascun forum
        member_counts = {}
        with driver.session(database="neo4j") as session:
            count_query = """
                MATCH (p:Person)-[:MEMBER_OF]->(f:Forum)
                WHERE f.id IN $forum_ids
                RETURN f.id AS forum_id, count(p) AS member_count
             """
            count_results = session.run(count_query, forum_ids=forum_ids)
            for record in count_results:
                member_counts[record["forum_id"]] = record["member_count"]

        # output
        results = []
        for forum in forum_docs:
            fid = forum["id"]
            results.append({
                "forum_id": fid,
                "title": forum.get("title"),
                "membership_creation_date": membership_dates.get(fid),
                "member_count": member_counts.get(fid, 0)
            })
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    

@app.get("/second_degree_commenters_on_liked_posts/{user_email}",
    response_model=List[SecondDegreeCommentResponse],
    summary="Find 2nd-degree connections who commented on posts liked by a user",
    tags=["Analysis"]
)
async def get_second_degree_commenters_on_liked_posts(
    user_email: str = Path(..., description="Email of the person to analyze", example="Jan16@hotmail.com")
):
    try:
        # Trova id user da email
        person_document = await db.person.find_one({"email": {"$in": [user_email]}})
        if not person_document:
            raise HTTPException(status_code=404, detail=f"Person with email '{user_email}' not found.")

        person_id = person_document.get("id") or str(person_document.get("_id"))
        if not person_id:
            raise HTTPException(status_code=500, detail="Person record exists but is missing an 'id'.")

        # Trova connessioni di 2°
        with driver.session(database="neo4j") as session:
            second_degree_query = """
                MATCH (p1:Person {id: $person_id})-[:KNOWS*2..2]-(p2:Person)
                RETURN DISTINCT p2.id AS second_person_id
             """
            second_degree_results = list(session.run(second_degree_query, person_id=person_id))

        if not second_degree_results:
            raise HTTPException(status_code=404, detail=f"No second-degree connections found for person with ID '{user_email}'.")

        # Trova i post che piacciono all'utente
        with driver.session(database="neo4j") as session:
            liked_posts_query = """
                MATCH (p1:Person {id: $person_id})-[:LIKES]->(post:Post)
                RETURN DISTINCT post.id AS liked_post_id
            """
            liked_posts_results = list(session.run(liked_posts_query, person_id=person_id))

        if not liked_posts_results:
            raise HTTPException(status_code=404,detail=f"No liked posts found for person with ID '{person_id}'.")

        second_degree_ids = [record["second_person_id"] for record in second_degree_results]
        liked_post_ids = [record["liked_post_id"] for record in liked_posts_results]

        # trova commenti scritti da connessioni 2° grado su post piaciuti all'utente
        comments = await db.comment.find({
            "CreatorPersonId": {"$in": second_degree_ids},
            "ParentPostId": {"$in": liked_post_ids}
        }).to_list(length=None)

        if not comments:
            raise HTTPException(status_code=404,detail="No comments found from second-degree connections on liked posts.")

        results = []
        # Recupera post una sola volta
        post_ids_set = list(set(comment["ParentPostId"] for comment in comments))
        posts = await db.post.find({"id": {"$in": post_ids_set}}).to_list(length=None)
        post_map = {post["id"]: post for post in posts}

        # Recupera persone una sola volta
        commenter_ids = list(set(comment["CreatorPersonId"] for comment in comments))
        people = await db.person.find({"id": {"$in": commenter_ids}}).to_list(length=None)
        person_map = {p["id"]: p.get("firstName", "") + " " + p.get("lastName", "") for p in people}

        for comment in comments:
            commenter_id = comment["CreatorPersonId"]
            post_id = comment["ParentPostId"]
            post = post_map.get(post_id)
            person_name = person_map.get(commenter_id, "Unknown")
            results.append({
                "post_id": post_id,
                "post_content": post.get("content") if post else None,
                "second_person_name": person_name,
                "comment_content": comment.get("content"),
            })
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    

@app.get("/common_interests_among_active_people/{organisation_name}",
         response_model=List[TagResponse],
         summary="Findi the top 10 most used tags by people who work or study in the same organsation.",
         tags=["Analysis"])
async def get_organisation_name(
    organisation_name: str = Path(..., description="Name of the organisation to analyze", example="UniTO"),
):
    try:
        # Ottengo la lista di id per un nome di organizzazione poichè ad esempio la stessa università potrebbe avere n id
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, "LocationPlaceId"
                FROM organization
                WHERE name = %s;
            """, (organisation_name,))
            organisationList = cursor.fetchall()
       
        if not organisationList:
            raise HTTPException(status_code=404,detail="Organisation not found.")
        
        organisation_ids = [row[0] for row in organisationList]  

        # Organisation in Neo è una unione di 'Company' e 'University'
        with driver.session() as session: 
            result = session.run("""
                MATCH (p:Person)-[:STUDY_AT|WORK_AT]->(o) 
                WHERE o.id IN $org_ids
                RETURN p.id AS person_id
            """, {"org_ids": organisation_ids})
            personInOrganisation = list(result)  
        
        if not personInOrganisation:
            raise HTTPException(status_code=404,detail="Person in organisation not found.")
        person_ids = [record["person_id"] for record in personInOrganisation]

        async def get_active_person_ids(person_ids: List[str]) -> List[str]:
            pipeline = [
                {"$match": {"CreatorPersonId": {"$in": person_ids}}},
                {"$group": {"_id": "$CreatorPersonId", "post_count": {"$sum": 1}}},
                {"$match": {"post_count": {"$gte": 10}}},
                {"$project": {"_id": 1}}
            ]
            cursor = db.post.aggregate(pipeline)
            results = []
            async for doc in cursor:
                results.append(doc["_id"])
            return results
        
        active_person_ids = await get_active_person_ids(person_ids)
        if not active_person_ids:
            raise HTTPException(status_code=404, detail="No active persons with ≥10 posts found.")

        with driver.session() as session:
            result = session.run("""
                MATCH (p:Person)-[:HAS_INTEREST]->(t:Tag)
                WHERE p.id IN $active_ids
                RETURN t.id AS tag_id, COUNT(*) AS usage_count
                ORDER BY usage_count DESC
                LIMIT 10
            """, {"active_ids": active_person_ids})
            interest_tag = [record.data() for record in result]
        print(interest_tag)
        tag_ids = [tag["tag_id"] for tag in interest_tag]
        query = """
             SELECT 
                t.id AS tag_id,
                t.name AS tag_name,
                t.url AS tag_url,
                tc.id AS class_id,
                tc.name AS class_name,
                tc.url AS class_url
            FROM tag t JOIN tagclass tc ON t."TypeTagClassId" = tc.id
            WHERE t.id = ANY(%s);
        """
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cursor:
            cursor.execute(query, (tag_ids,))
            tag_details = cursor.fetchall()

        # Mappa tag_id → usage_count
        usage_map = {tag["tag_id"]: tag["usage_count"] for tag in interest_tag}

        final_results = []
        for row in tag_details:
            tag_id = row["tag_id"]
            final_results.append(TagResponse(
                tag_id=tag_id,
                tag_name=row["tag_name"],
                tag_url=row["tag_url"],
                class_id=row["class_id"],
                class_name=row["class_name"],
                class_url=row["class_url"],
                usage_count=usage_map.get(tag_id, 0)
                ))
        # Ordina i risultati finali per usage_count decrescente
        final_results.sort(key=lambda x: x.usage_count, reverse=True)

        return final_results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")