import os
from dotenv import load_dotenv
from neo4j import GraphDatabase

from db.initialize_db.init_neo4j_nodes import likes_post_files, likes_comment_files, has_interest_files, member_of_files, \
    forum_has_tag_files, post_has_tag_files, comment_has_tag_files, study_at_files, work_at_files, knows_files


def create_relationships(driver, files, from_entity, to_entity, from_field, to_field, rel_type, props=None):
    with driver.session() as session:
        for file in files:
            print(f"Processing relationship file: {file}")
            try:
                prop_str = ''
                if props:
                    prop_str = ', ' + ', '.join([f"{k}: row.{k}" for k in props])

                session.run(f"""
                LOAD CSV WITH HEADERS FROM 'file:///{file}' AS row FIELDTERMINATOR '|'
                CALL (row) {{
                    WITH row
                    MATCH (a:{from_entity} {{id: toInteger(row.{from_field})}})
                    MATCH (b:{to_entity} {{id: toInteger(row.{to_field})}})
                    MERGE (a)-[r:{rel_type} {{creationDate: row.creationDate{prop_str}}}]->(b)
                }} IN TRANSACTIONS OF 1000 ROWS
                """)
                print(f"Successfully created {rel_type} relationships from {file}")
            except Exception as e:
                print(f"Error processing relationship file {file}: {e}")


def main():
    load_dotenv()
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")
    driver = GraphDatabase.driver(uri, auth=(user, password))

    # Reuse file lists
    create_relationships(driver, post_has_tag_files, "Post", "Tag", "PostId", "TagId", "HAS_TAG")
    create_relationships(driver, knows_files, "Person", "Person", "Person1Id", "Person2Id", "KNOWS")
    create_relationships(driver, likes_post_files, "Person", "Post", "PersonId", "PostId", "LIKES")
    create_relationships(driver, likes_comment_files, "Person", "Comment", "PersonId", "CommentId", "LIKES")
    create_relationships(driver, has_interest_files, "Person", "Tag", "PersonId", "TagId", "HAS_INTEREST")
    create_relationships(driver, member_of_files, "Person", "Forum", "PersonId", "ForumId", "MEMBER_OF")
    create_relationships(driver, forum_has_tag_files, "Forum", "Tag", "ForumId", "TagId", "HAS_TAG")
    create_relationships(driver, post_has_tag_files, "Post", "Tag", "PostId", "TagId", "HAS_TAG")
    create_relationships(driver, comment_has_tag_files, "Comment", "Tag", "CommentId", "TagId", "HAS_TAG")
    create_relationships(driver, study_at_files, "Person", "University", "PersonId", "UniversityId", "STUDY_AT",
                         ["classYear"])
    create_relationships(driver, work_at_files, "Person", "Company", "PersonId", "CompanyId", "WORK_AT", ["workFrom"])

    driver.close()


if __name__ == "__main__":
    main()
