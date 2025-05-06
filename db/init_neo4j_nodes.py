import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

constraints = [
    "CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT post_id IF NOT EXISTS FOR (p:Post) REQUIRE p.id IS UNIQUE",
    "CREATE CONSTRAINT comment_id IF NOT EXISTS FOR (c:Comment) REQUIRE c.id IS UNIQUE",
    "CREATE CONSTRAINT tag_id IF NOT EXISTS FOR (t:Tag) REQUIRE t.id IS UNIQUE",
    "CREATE CONSTRAINT forum_id IF NOT EXISTS FOR (f:Forum) REQUIRE f.id IS UNIQUE",
    "CREATE CONSTRAINT university_id IF NOT EXISTS FOR (u:University) REQUIRE u.id IS UNIQUE",
    "CREATE CONSTRAINT company_id IF NOT EXISTS FOR (c:Company) REQUIRE c.id IS UNIQUE"
]

def create_constraints(driver):
    with driver.session() as session:
        for c in constraints:
            session.run(c)



def create_nodes(driver, files, entity1, entity2, id_field1, id_field2):
    with driver.session() as session:
        for file in files:
            print(f"Processing file: {file}")
            try:
                session.run(f"""
                LOAD CSV WITH HEADERS FROM 'file:///{file}' AS row FIELDTERMINATOR '|'
                CALL (row) {{
                    WITH row
                    MERGE (e1:{entity1} {{id: toInteger(row.{id_field1})}})
                    MERGE (e2:{entity2} {{id: toInteger(row.{id_field2})}})
                }} IN TRANSACTIONS OF 1000 ROWS
                """)
                print(f"Successfully processed file: {file}")
            except Exception as e:
                print(f"Error processing file {file}: {e}")

def create_single_node(driver, files, entity, id_field):
    with driver.session() as session:
        for file in files:
            print(f"Processing file: {file}")
            try:
                session.run(f"""
                LOAD CSV WITH HEADERS FROM 'file:///{file}' AS row FIELDTERMINATOR '|'
                CALL (row) {{
                    WITH row
                    MERGE (e:{entity} {{id: toInteger(row.{id_field})}})
                }} IN TRANSACTIONS OF 1000 ROWS
                """)
                print(f"Successfully processed file: {file}")
            except Exception as e:
                print(f"Error processing file {file}: {e}")

def main():
    load_dotenv()
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    driver = GraphDatabase.driver(uri, auth=(user, password))

    create_constraints(driver)

    create_nodes(driver, knows_files, "Person", "Person", "Person1Id", "Person2Id")
    create_nodes(driver, likes_post_files, "Person", "Post", "PersonId", "PostId")
    create_nodes(driver, likes_comment_files, "Person", "Comment", "PersonId", "CommentId")
    create_nodes(driver, has_interest_files, "Person", "Tag", "PersonId", "TagId")
    create_nodes(driver, member_of_files, "Forum", "Person", "ForumId", "PersonId")
    create_nodes(driver, forum_has_tag_files, "Forum", "Tag", "ForumId", "TagId")
    create_nodes(driver, post_has_tag_files, "Post", "Tag", "PostId", "TagId")
    create_nodes(driver, comment_has_tag_files, "Comment", "Tag", "CommentId", "TagId")
    create_nodes(driver, study_at_files, "Person", "University", "PersonId", "UniversityId")
    create_nodes(driver, work_at_files, "Person", "Company", "PersonId", "CompanyId")

    driver.close()

# Files
knows_files = [
    "Person_knows_Person/part-00000-229ad475-a3b7-4391-b675-22ef679b777a-c000.csv",
    "Person_knows_Person/part-00002-229ad475-a3b7-4391-b675-22ef679b777a-c000.csv",
    "Person_knows_Person/part-00003-229ad475-a3b7-4391-b675-22ef679b777a-c000.csv"
]

likes_post_files = [
    "Person_likes_Post/part-00000-1db05b26-d9eb-4e65-be18-f0d7bf575214-c000.csv",
    "Person_likes_Post/part-00001-1db05b26-d9eb-4e65-be18-f0d7bf575214-c000.csv",
    "Person_likes_Post/part-00004-1db05b26-d9eb-4e65-be18-f0d7bf575214-c000.csv",
    "Person_likes_Post/part-00003-1db05b26-d9eb-4e65-be18-f0d7bf575214-c000.csv"
]

likes_comment_files = [
    "Person_likes_Comment/part-00000-954d02cd-1f9b-478b-9d9d-db930cdfc2a0-c000.csv",
    "Person_likes_Comment/part-00003-954d02cd-1f9b-478b-9d9d-db930cdfc2a0-c000.csv",
    "Person_likes_Comment/part-00001-954d02cd-1f9b-478b-9d9d-db930cdfc2a0-c000.csv",
    "Person_likes_Comment/part-00006-954d02cd-1f9b-478b-9d9d-db930cdfc2a0-c000.csv"
]

has_interest_files = [
    "Person_hasInterest_Tag/part-00000-2041dc2e-354d-4676-ae8d-30d68582065d-c000.csv",
    "Person_hasInterest_Tag/part-00002-2041dc2e-354d-4676-ae8d-30d68582065d-c000.csv",
    "Person_hasInterest_Tag/part-00001-2041dc2e-354d-4676-ae8d-30d68582065d-c000.csv"
]

member_of_files = [
    "Forum_hasMember_Person/part-00000-093f0797-e3d2-4e9a-aadf-c0c957b6c78b-c000.csv",
    "Forum_hasMember_Person/part-00007-093f0797-e3d2-4e9a-aadf-c0c957b6c78b-c000.csv",
    "Forum_hasMember_Person/part-00003-093f0797-e3d2-4e9a-aadf-c0c957b6c78b-c000.csv",
    "Forum_hasMember_Person/part-00004-093f0797-e3d2-4e9a-aadf-c0c957b6c78b-c000.csv",
    "Forum_hasMember_Person/part-00006-093f0797-e3d2-4e9a-aadf-c0c957b6c78b-c000.csv",
    "Forum_hasMember_Person/part-00001-093f0797-e3d2-4e9a-aadf-c0c957b6c78b-c000.csv"
]

forum_has_tag_files = [
    "Forum_hasTag_Tag/part-00000-1e403b78-d38e-4ba4-86a6-ebe2a8716214-c000.csv",
    "Forum_hasTag_Tag/part-00002-1e403b78-d38e-4ba4-86a6-ebe2a8716214-c000.csv",
    "Forum_hasTag_Tag/part-00001-1e403b78-d38e-4ba4-86a6-ebe2a8716214-c000.csv"
]

post_has_tag_files = [
    "Post_hasTag_Tag/part-00000-a181a312-c991-4be8-a0f6-b834b5e7a007-c000.csv",
    "Post_hasTag_Tag/part-00002-a181a312-c991-4be8-a0f6-b834b5e7a007-c000.csv",
    "Post_hasTag_Tag/part-00003-a181a312-c991-4be8-a0f6-b834b5e7a007-c000.csv"
]

comment_has_tag_files = [
    "Comment_hasTag_Tag/part-00000-6d6a9272-6c6e-48d9-a422-097c72739bdf-c000.csv",
    "Comment_hasTag_Tag/part-00001-6d6a9272-6c6e-48d9-a422-097c72739bdf-c000.csv",
    "Comment_hasTag_Tag/part-00005-6d6a9272-6c6e-48d9-a422-097c72739bdf-c000.csv",
    "Comment_hasTag_Tag/part-00003-6d6a9272-6c6e-48d9-a422-097c72739bdf-c000.csv",
    "Comment_hasTag_Tag/part-00006-6d6a9272-6c6e-48d9-a422-097c72739bdf-c000.csv"
]

study_at_files = [
    "Person_studyAt_University/part-00000-773dbdd3-733c-447e-90ed-2679590b2d7f-c000.csv",
    "Person_studyAt_University/part-00002-773dbdd3-733c-447e-90ed-2679590b2d7f-c000.csv",
    "Person_studyAt_University/part-00001-773dbdd3-733c-447e-90ed-2679590b2d7f-c000.csv"
]

work_at_files = [
    "Person_workAt_Company/part-00000-bce1dbfa-615a-4937-9a34-ad626a3c454a-c000.csv",
    "Person_workAt_Company/part-00002-bce1dbfa-615a-4937-9a34-ad626a3c454a-c000.csv",
    "Person_workAt_Company/part-00001-bce1dbfa-615a-4937-9a34-ad626a3c454a-c000.csv"
]

if __name__ == "__main__":
    main()
