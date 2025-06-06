from fastapi import APIRouter, HTTPException, Path, Query, Depends

import psycopg2, math
from psycopg2.extras import DictCursor

from db.mongo_client import db
from db.neo4j_client import driver
from db.postgres_client import get_db_connection

from models.query_1.model import PostResponse
from models.query_2.model import ForumResponse
from models.query_3.model import FullResponseItem
from models.query_4.model import GroupDetail, MemberInfo
from models.query_5.model import SecondDegreeCommentResponse

from typing import List, Optional


router = APIRouter()


# --- 1. Endpoint for finding posts by user email ---
@router.get("/by-email/{user_email}",
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


# --- 2. Endpoint for finding forum by user email ---
@router.get("/forumsEmail/{user_email}",
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

        # Maps {forum_id: creation_date}
        membership_dates = {
            record["forum_id"]: record["membership_creation_date"]
            for record in neo4j_results
        }

        # Count number for each forum 
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

        results = []
        for forum in forum_docs:
            fid = forum["id"]
            results.append({
                "forum_id": fid,
                "title": forum.get("title"),
                "membership_creation_date": membership_dates.get(fid),
                "member_count": member_counts.get(fid, 0)
            })
        results.sort(key=lambda x: x["membership_creation_date"])
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# --- 3. Endpoint for finding persons who know and commented by user email ---
@router.get("/find-person/by-email/{target_email}",
            response_model=List[FullResponseItem],
            summary="Find all person who know and have commented a user target post",
            tags=["Persons"])
async def find_person_who_know_and_commented(
        target_email: str = Path(..., description="An email address of the target user.", example="Jeorge74@gmail.com")
):
    try:
        # 1. Find target person
        target_person = await db.person.find_one({"email": target_email})
        if not target_person:
            raise HTTPException(status_code=404, detail=f"Person with email '{target_email}' not found.")
        
        target_id = target_person.get("id") or str(target_person.get("_id"))
        if not target_id:
            raise HTTPException(status_code=500, detail="Person record exists but is missing an 'id'.")

        # 2. Find all posts created by target user
        target_posts = await db.post.find({"CreatorPersonId": target_id}).to_list(length=None)
        post_ids = [post["id"] for post in target_posts]
        if not post_ids:
            return []

        post_map = {post["id"]: post for post in target_posts}

        # 3. Find all comments on target posts
        comments = await db.comment.find({"ParentPostId": {"$in": post_ids}}).to_list(length=None)
        commenter_map = {}
        for comment in comments:
            commenter_id = comment["CreatorPersonId"]
            commenter_map.setdefault(commenter_id, []).append(comment)

        if not commenter_map:
            return []
        commenter_ids = list(commenter_map.keys())

        # 4. Use Neo4j to find which commenters know the target person
        with driver.session(database="neo4j") as session:
            query = """
            MATCH (a:Person {id: $target_id})-[:KNOWS]->(b:Person)
            WHERE b.id IN $commenter_ids
            RETURN b.id AS id
            """
            result = session.run(query, {
                "target_id": target_id,
                "commenter_ids": commenter_ids
            })
            known_ids = {record["id"] for record in result}
        if not known_ids:
            return []

        # 5. Get knowing persons from MongoDB in bulk
        knowing_people = await db.person.find({"id": {"$in": list(known_ids)}}).to_list(length=None)
        knowing_people_map = {p["id"]: p for p in knowing_people}

        # 6. Compose results
        results = []
        for commenter_id in known_ids:
            knowing_person = knowing_people_map.get(commenter_id)
            if not knowing_person:
                continue
            user_comments = commenter_map.get(commenter_id, [])
            commented_post_ids = [c["ParentPostId"] for c in user_comments]

            forum_ids = list({
                post_map[pid]["ContainerForumId"]
                for pid in commented_post_ids
                if pid in post_map and post_map[pid].get("ContainerForumId")
            })
            forums = await db.forum.find({"id": {"$in": forum_ids}}).to_list(length=None)

            results.append({
                "target_person": target_person,
                "knowing_person": knowing_person,
                "comments": [
                    {
                        **comment,
                        "post": {
                            **post_map.get(comment["ParentPostId"], {}),
                            "forum_id": post_map.get(comment["ParentPostId"], {}).get("ContainerForumId")
                        }
                    }
                    for comment in user_comments
                ],
                "forums": forums
            })
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")


# --- Helper function for Neo4j results ---
def get_neo4j_results(tx, query, params):
    result = tx.run(query, params)
    return [record.data() for record in result]


# --- 4. Endpoint for finding Find Groups by Work & Forum ---
@router.get(
    "/groups/by-company/{company_name}/year/{target_year}",  # URL più RESTful
    response_model=List[GroupDetail],
    summary="Find groups of people by specific company (from yean) and shared forum",
    tags=["Complex Queries - Specific Company"]
)
async def find_groups_for_specific_company(
        company_name: str = Path(..., description="Name of target company"),
        target_year: int = Path(...,
                                description="Year",
                                ge=1900, le=2100),
        limit: Optional[int] = Query(50, description="Maximium number of forum groups to return for this company",
                                     ge=1, le=1000),
        pg_conn: psycopg2.extensions.connection = Depends(get_db_connection)
):

    company_psql_id = None
    try:
        with pg_conn.cursor(cursor_factory=DictCursor) as cursor:
            cursor.execute("SELECT id FROM organization WHERE name = %s", (company_name,))
            company_row = cursor.fetchone()
            if company_row:
                company_psql_id = company_row["id"]
            else:
                raise HTTPException(status_code=404, detail=f"Azienda con nome '{company_name}' non trovata.")
        pg_conn.commit()  # Commit dopo la lettura, buona pratica

    except psycopg2.Error as e:
        print(f"ERROR: PostgreSQL error while searching for company ID of '{company_name}': {e}")
        if pg_conn: pg_conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error while comapny research: {e}")

    # Step 2: executing Neo4j Query
    # Using two-stage query which worked well without problematic indexes but now filtered for $companyIdParam
    cypher_query_specific_company = """
    MATCH (person:Person)-[workRel:WORK_AT]->(company:Company {id: $companyIdParam}),
          (person)-[:MEMBER_OF]->(forum:Forum)
    WHERE workRel.workFrom IS NOT NULL AND workRel.workFrom <= $targetYear
    WITH company, forum, count(person) AS groupSizeCalc
    WHERE groupSizeCalc > 1

    MATCH (p:Person)-[w:WORK_AT]->(company), // company è già filtrata per id
          (p)-[:MEMBER_OF]->(forum)
    WHERE w.workFrom IS NOT NULL AND w.workFrom <= $targetYear
    WITH company, forum, collect(p.id) AS personMongoIds // groupSizeCalc non serve più qui
    ORDER BY forum.id // Ordina per ID del forum per risultati consistenti
    RETURN company.id AS companyPsqlId, // Sarà sempre $companyIdParam
           forum.id AS forumMongoId,
           personMongoIds
    LIMIT $limitParam
    """
    neo4j_params = {
        "companyIdParam": company_psql_id,
        "targetYear": target_year,
        "limitParam": limit
    }

    final_group_details_specific = []

    try:
        with driver.session(database="neo4j") as session:
            raw_groups_from_neo4j = session.read_transaction(get_neo4j_results, cypher_query_specific_company,
                                                             neo4j_params)

        if not raw_groups_from_neo4j:
            return []  

        # Step 3, 4, 5: Preparation and retrieve of details batch (Forum and People)
        all_forum_ids = list(set(g["forumMongoId"] for g in raw_groups_from_neo4j))
        all_person_ids_flat = list(set(pid for g in raw_groups_from_neo4j for pid in g["personMongoIds"]))


        forum_details_map = {}
        if all_forum_ids:
            forum_cursor = db.forum.find({"id": {"$in": all_forum_ids}}, {"id": 1, "title": 1})
            async for forum_doc in forum_cursor:
                forum_details_map[forum_doc["id"]] = forum_doc.get("title", "Forum Sconosciuto")

        person_details_map = {}
        if all_person_ids_flat:
            person_cursor = db.person.find(
                {"id": {"$in": all_person_ids_flat}},
                {"id": 1, "firstName": 1, "lastName": 1, "email": 1, "_id": 0}
            )
            async for person_doc in person_cursor:
                person_details_map[person_doc["id"]] = MemberInfo(**person_doc)

        # Assembling final results
        for group_skeleton in raw_groups_from_neo4j:
            # company_id_from_skel = group_skeleton["companyPsqlId"]
            forum_id = group_skeleton["forumMongoId"]

            # Using given company_name
            forum_title = forum_details_map.get(forum_id, "Forum Sconosciuto")

            current_members_info = []
            for person_id in group_skeleton["personMongoIds"]:
                member_info = person_details_map.get(person_id)
                if member_info:
                    current_members_info.append(member_info)

            if current_members_info:
                final_group_details_specific.append(GroupDetail(
                    companyId=company_psql_id,  # Using verified company ID
                    companyName=company_name,  # Using given company name
                    forumId=forum_id,
                    forumTitle=forum_title,
                    members=current_members_info
                ))

    except HTTPException:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

    return final_group_details_specific


# --- 5. Endpoint for finding 2nd-degree connections who commented on posts liked by a user ---
@router.get("/second_degree_commenters_on_liked_posts/{user_email}",
    response_model=List[SecondDegreeCommentResponse],
    summary="Find 2nd-degree connections who commented on posts liked by a user",
    tags=["Analysis"]
)
async def get_second_degree_commenters_on_liked_posts(
    user_email: str = Path(..., description="Email of the person to analyze", example="Jan16@hotmail.com")
):
    try:
        # Find id user by mail
        person_document = await db.person.find_one({"email": {"$in": [user_email]}})
        if not person_document:
            raise HTTPException(status_code=404, detail=f"Person with email '{user_email}' not found.")

        person_id = person_document.get("id") or str(person_document.get("_id"))
        if not person_id:
            raise HTTPException(status_code=500, detail="Person record exists but is missing an 'id'.")

        # Find second-degree connection
        with driver.session(database="neo4j") as session:
            second_degree_query = """
                MATCH (p1:Person {id: $person_id})-[:KNOWS*2..2]-(p2:Person)
                RETURN DISTINCT p2.id AS second_person_id
             """
            second_degree_results = list(session.run(second_degree_query, person_id=person_id))

        if not second_degree_results:
            raise HTTPException(status_code=404, detail=f"No second-degree connections found for person with ID '{user_email}'.")

        # Find posts liked by user
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

        # Find comments write by second-degree connections on posts liked by user
        comments = await db.comment.find({
            "CreatorPersonId": {"$in": second_degree_ids},
            "ParentPostId": {"$in": liked_post_ids}
        }).to_list(length=None)

        if not comments:
            raise HTTPException(status_code=404,detail="No comments found from second-degree connections on liked posts.")

        results = []
        # Retrieve post once
        post_ids_set = list(set(comment["ParentPostId"] for comment in comments))
        posts = await db.post.find({"id": {"$in": post_ids_set}}).to_list(length=None)
        post_map = {post["id"]: post for post in posts}

        def is_empty(value):
            return (
                value is None or 
                value == "" or 
                (isinstance(value, float) and math.isnan(value))
            )

        # Retrieve people once
        commenter_ids = list(set(comment["CreatorPersonId"] for comment in comments))
        people = await db.person.find({"id": {"$in": commenter_ids}}).to_list(length=None)
        person_map = {p["id"]: p.get("firstName", "") + " " + p.get("lastName", "") for p in people}

        for comment in comments:
            commenter_id = comment["CreatorPersonId"]
            post_id = comment["ParentPostId"]
            post = post_map.get(post_id)
            person_name = person_map.get(commenter_id, "Unknown")
            content = post.get("content")
            image = post.get("imageFile")
            if is_empty(content) and not is_empty(image):
                post_content = image
            elif not is_empty(content):
                post_content = content
            else:
                post_content = None
            results.append({
                "post_id": post_id,
                "post_content": post_content,
                "second_person_name": person_name,
                "comment_content": comment.get("content"),
            })
        return results

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")