from fastapi import APIRouter, HTTPException
import psycopg
import psycopg2
from fastapi import HTTPException, Path, Depends, Query  # Added Path
from db.mongo_client import db
from db.neo4j_client import driver
from db.postgres_client import conn, get_db_connection  # Assuming conn is your psycopg connection pool or similar
from models.query_6.model import FindCities
from models.query_7.model import MostUsedTagsResponse, get_most_used_tags_by_city_interest
from models.query_8.model import TagResponse
from models.query_9.model import FindForumResponse
from typing import List, Annotated # Ensure Annotated is imported


router = APIRouter()


# --- 6. Endpoint for finding cities of active people ---
@router.get("/find-cities/by-activeuser",
            response_model=List[FindCities],
            summary="Find cities with at least N active users",
            tags=["Cities"])
async def get_cities_with_active_users(
    min_active_people: int = Query(..., ge=1, description="Minimum number of active users per city."),
):
    try:
        # 1. Aggregate user's posts
        post_counts = await db.post.aggregate([
            {"$group": {"_id": "$CreatorPersonId", "postCount": {"$sum": 1}}}
        ]).to_list(length=None)

        # 2. Aggregate user's comments
        comment_counts = await db.comment.aggregate([
            {"$group": {"_id": "$CreatorPersonId", "commentCount": {"$sum": 1}}}
        ]).to_list(length=None)

        # 3. Combine posts + comments
        activity_map = {}
        for doc in post_counts:
            activity_map[doc["_id"]] = doc["postCount"]
        for doc in comment_counts:
            activity_map[doc["_id"]] = activity_map.get(doc["_id"], 0) + doc["commentCount"]

        # 4. Filter active users (at least 5 activities)
        active_user_ids = [uid for uid, count in activity_map.items() if count >= 5]
        if not active_user_ids:
            return []

        # 5. Find LocationCityId of active people
        city_counts = {}
        async for person in db.person.find({"id": {"$in": active_user_ids}}, {"LocationCityId": 1}):
            city_id = person.get("LocationCityId")
            if city_id is not None:
                city_counts[city_id] = city_counts.get(city_id, 0) + 1

        # 6. Filter cities with at least min_active_people active users
        filtered_city_ids = [cid for cid, count in city_counts.items() if count >= min_active_people]
        if not filtered_city_ids:
            return []
        
        # 7. Get cities names from PostgreSQL
        with conn.cursor() as cur:
            cur.execute(
                '''
                SELECT id, name
                FROM "place"
                WHERE id = ANY(%s)
                ''',
                (filtered_city_ids,)
            )
            city_names = {row[0]: row[1] for row in cur.fetchall()}

        # 8. Final results
        result = []
        for city_id in filtered_city_ids:
            result.append({
                "cityId": city_id,
                "cityName": city_names.get(city_id, "Unknown"),
                "activeUserCount": city_counts[city_id]
            })
        return result

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
    

# --- 7. Endpoint for finding Most Used Tags by City Interest ---
@router.get(
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


# --- 8. Endpoint for finding top 10 most used tags by people in same organisation. ---
@router.get("/common_interests_among_active_people/{organisation_name}",
         response_model=List[TagResponse],
         summary="Findi the top 10 most used tags by people who work or study in the same organsation.",
         tags=["Analysis"])
async def get_organisation_name(
    organisation_name: str = Path(..., description="Name of the organisation to analyze", example="UniTO"),
):
    try:
        # Get the id list for an organization name because for example the same university could have n id
        with conn.cursor() as cursor:
            cursor.execute("""
                SELECT id, LocationPlaceId
                FROM organization
                WHERE name = %s;
            """, (organisation_name,))
            organisationList = cursor.fetchall()
       
        if not organisationList:
            raise HTTPException(status_code=404,detail="Organisation not found.")
        
        organisation_ids = [row[0] for row in organisationList]  

        # Neo's organisation is a union of 'Company' and 'University'
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
            FROM tag t JOIN tagclass tc ON t.TypeTagClassId = tc.id
            WHERE t.id = ANY(%s);
        """
        with conn.cursor(row_factory=psycopg.rows.dict_row) as cursor:
            cursor.execute(query, (tag_ids,))
            tag_details = cursor.fetchall()

        # Maps tag_id → usage_count
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
        # Sort final results by usage_count decreasing
        final_results.sort(key=lambda x: x.usage_count, reverse=True)
        return final_results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# --- 9. Endpoint for finding forums of member interested in same tag class ---
@router.get("/find-forum/by-tagclass/{tagclass_name}",
            response_model=List[FindForumResponse],
            summary="Find all forums with at least X members interested in tags of the same tagClass",
            tags=["Forums"])
async def get_forums_by_tagclass_members(
        tagclass_name: str = Path(..., description="Name of the tagClass of members interested in"),
        min_members: int = Query(..., description="Minimum number of members interested in the same tagClass.")
):
    try:
        # 1. Get tag IDs for the given tag class on PostgreSQL
        with conn.cursor() as cur:
            cur.execute('''
                SELECT t.id
                FROM "tag" t
                JOIN "tagclass" tc ON t."typetagclassid" = tc.id
                WHERE tc.name = %s
            ''', (tagclass_name,))
            tag_rows = cur.fetchall()
            tag_ids = [row[0] for row in tag_rows]
            if not tag_ids:
                raise HTTPException(status_code=404, detail=f"No Tag found for TagClass '{tagclass_name}'")
        
        with driver.session(database="neo4j") as session:
            result = session.run(
                '''
                MATCH (p:Person)-[:HAS_INTEREST]->(t:Tag)
                WHERE t.id IN $tag_ids
                MATCH (p)-[:MEMBER_OF]->(f:Forum)
                WITH f.id AS forum_id, COUNT(DISTINCT p) AS interested_members
                WHERE interested_members >= $min_members
                RETURN forum_id, interested_members
                ''',
                parameters={"tag_ids": tag_ids, "min_members": min_members}
            )
            forum_infos = [{"forum_id": record["forum_id"], "interested_members": record["interested_members"]} for record in result]
            forum_ids = [info["forum_id"] for info in forum_infos]
        if not forum_ids:
            return []
        
        # 3. Get forum from MongoDB with IDs
        forum_docs = await db.forum.find({"id": {"$in": forum_ids}}).to_list(length=None)
        for forum in forum_docs:
            forum["_id"] = str(forum["_id"])  # Manage ObjectId if necessary
            forum_id = forum.get("id")
            # Trova interested_members associato a quel forum_id
            matching_info = next((info for info in forum_infos if info["forum_id"] == forum_id), None)
            forum["interested_members"] = matching_info["interested_members"] if matching_info else 0
        return forum_docs

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")