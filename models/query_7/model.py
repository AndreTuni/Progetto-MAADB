from pydantic import BaseModel, Field
from typing import List, Optional
import psycopg2
from psycopg2.extras import DictCursor


# Pydantic Models for Query 7
class TagUsage(BaseModel):
    tag_name: str
    count: int
    tag_url: Optional[str] = None
    tag_class_name: Optional[str] = None


class MostUsedTagsResponse(BaseModel):
    user_email: str
    city_name: Optional[str] = None
    tags: List[TagUsage]
    message: Optional[str] = None


async def get_most_used_tags_by_city_interest(
        user_email: str,
        top_n: int,
        mongo_db_async,
        neo4j_driver_sync,
        pg_conn_sync
) -> MostUsedTagsResponse:
    # ... (Steps 1, 2, city name fetching remain the same, ensure they are working) ...
    person_doc = await mongo_db_async.person.find_one(
        {"email": user_email},
        {"LocationCityId": 1, "id": 1, "_id": 0}
    )

    if not person_doc:
        return MostUsedTagsResponse(user_email=user_email, tags=[],
                                    message=f"User with email '{user_email}' not found.")
    city_id = person_doc.get("LocationCityId")
    city_name_display = None
    if city_id is None:
        return MostUsedTagsResponse(user_email=user_email, tags=[],
                                    message=f"User '{user_email}' found, but LocationCityId is missing.")
    try:
        with pg_conn_sync.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT name FROM place WHERE id = %s", (city_id,))
            city_record = cursor.fetchone()
            city_name_display = city_record["name"] if city_record else f"Unknown City (ID: {city_id})"
    except Exception as e:
        print(f"Error fetching city name for ID {city_id}: {e}")
        city_name_display = f"Error for City ID: {city_id}"

    persons_in_city_cursor = mongo_db_async.person.find({"LocationCityId": city_id}, {"id": 1, "_id": 0})
    person_ids_in_city = [p["id"] async for p in persons_in_city_cursor if "id" in p]
    if not person_ids_in_city:
        return MostUsedTagsResponse(user_email=user_email, city_name=city_name_display, tags=[],
                                    message=f"User '{user_email}' is in {city_name_display}, but no other persons found in this city.")

    tag_counts_from_neo4j = []
    neo4j_query = """
    MATCH (p:Person)-[:HAS_INTEREST]->(t:Tag)
    WHERE p.id IN $personIds
    RETURN t.id AS tagId, count(t) AS interestCount
    ORDER BY interestCount DESC, t.id ASC
    LIMIT $limit
    """
    try:
        with neo4j_driver_sync.session(database="neo4j") as session:
            results = session.run(neo4j_query, personIds=person_ids_in_city, limit=top_n)
            for record in results:
                tag_counts_from_neo4j.append({"tag_id": record["tagId"], "count": record["interestCount"]})
    except Exception as e:
        print(f"Neo4j error: {e}")
        return MostUsedTagsResponse(user_email=user_email, city_name=city_name_display, tags=[],
                                    message=f"Neo4j error: {str(e)}")

    if not tag_counts_from_neo4j:
        return MostUsedTagsResponse(user_email=user_email, city_name=city_name_display, tags=[],
                                    message=f"No tags found by interest for people in {city_name_display}.")

    tag_ids_to_fetch_details = [tc["tag_id"] for tc in tag_counts_from_neo4j]

    tag_details_map = {}
    pg_error_message = None  # To store any PG error for the main response

    if tag_ids_to_fetch_details:
        try:
            with pg_conn_sync.cursor(cursor_factory=DictCursor) as cursor:
                placeholders = ', '.join(['%s'] * len(tag_ids_to_fetch_details))
                pg_query = f"""
                SELECT t.id, t.name AS tag_name, t.url AS tag_url, tc.name AS tag_class_name
                FROM tag t
                LEFT JOIN tagclass tc ON t.TypeTagClassId = tc.id
                WHERE t.id IN ({placeholders})
                """
                cursor.execute(pg_query, tuple(tag_ids_to_fetch_details))
                fetched_rows = cursor.fetchall()
                for row in fetched_rows:
                    tag_details_map[row["id"]] = {
                        "name": row["tag_name"],
                        "url": row["tag_url"],
                        "class_name": row["tag_class_name"]
                    }
            # No commit needed for SELECT
        except psycopg2.Error as e:
            pg_error_message = f"PostgreSQL error fetching tag details: {str(e)}"
            print(pg_error_message)  # Log to server console
            if pg_conn_sync: pg_conn_sync.rollback()
        except Exception as e:
            pg_error_message = f"Unexpected error with PostgreSQL fetching tag details: {str(e)}"
            print(pg_error_message)  # Log to server console
            if pg_conn_sync: pg_conn_sync.rollback()

    final_tags_usage: List[TagUsage] = []
    for tc_info in tag_counts_from_neo4j:
        tag_id = tc_info["tag_id"]
        details = tag_details_map.get(tag_id)

        if details:
            final_tags_usage.append(TagUsage(
                tag_name=details["name"] if details["name"] else f"Tag ID: {tag_id} (Name N/A)",
                # Handle if name itself is null
                count=tc_info["count"],
                tag_url=details["url"],
                tag_class_name=details["class_name"]
            ))
        else:
            # This case is hit if tag_id from Neo4j was not found in tag_details_map
            # which means it wasn't in PG or PG query failed for it.
            print(f"DEBUG: No details found in tag_details_map for tag_id: {tag_id}")  # DEBUG PRINT
            final_tags_usage.append(TagUsage(
                tag_name=f"Tag ID: {tag_id} (Details N/A from PG)",
                count=tc_info["count"]
            ))

    response_message = "Successfully retrieved tag usage."
    if pg_error_message:
        response_message = f"Retrieved tags, but encountered an issue: {pg_error_message}"
    elif not final_tags_usage and tag_counts_from_neo4j:  # Neo4j found tags, but PG mapping failed for all
        response_message = "Tags found by interest, but failed to map details for any from PostgreSQL."
    elif not final_tags_usage:  # No tags from Neo4j to begin with
        response_message = f"No tags found by interest for people in {city_name_display}."

    return MostUsedTagsResponse(
        user_email=user_email,
        city_name=city_name_display,
        tags=final_tags_usage,
        message=response_message
    )