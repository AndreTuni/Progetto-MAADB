from neo4j import GraphDatabase
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class Neo4jImporter:
    def __init__(self, uri, user, password):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))

    def close(self):
        self.driver.close()

    def create_constraints(self):
        with self.driver.session() as session:
            # Create constraints for all node types
            constraints = [
                "CREATE CONSTRAINT person_id IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT post_id IF NOT EXISTS FOR (p:Post) REQUIRE p.id IS UNIQUE",
                "CREATE CONSTRAINT comment_id IF NOT EXISTS FOR (c:Comment) REQUIRE c.id IS UNIQUE",
                "CREATE CONSTRAINT tag_id IF NOT EXISTS FOR (t:Tag) REQUIRE t.id IS UNIQUE",
                "CREATE CONSTRAINT forum_id IF NOT EXISTS FOR (f:Forum) REQUIRE f.id IS UNIQUE",
                "CREATE CONSTRAINT university_id IF NOT EXISTS FOR (u:University) REQUIRE u.id IS UNIQUE",
                "CREATE CONSTRAINT company_id IF NOT EXISTS FOR (c:Company) REQUIRE c.id IS UNIQUE"
            ]

            for constraint in constraints:
                session.run(constraint)
                logger.info(f"Created constraint: {constraint}")

    def create_person_knows_person_nodes(self, tx, filepath):
        query = f"""
        LOAD CSV WITH HEADERS FROM '{filepath}' AS row
        MERGE (p1:Person {{id: toInteger(row.Person1Id)}})
        MERGE (p2:Person {{id: toInteger(row.Person2Id)}})
        """
        try:
            tx.run(query)
            logger.info(f"Created Person nodes from: {filepath}")
        except Exception as e:
            logger.error(f"Error creating Person nodes from {filepath}: {str(e)}")

    def create_person_likes_post_nodes(self, tx, filepath):
        query = f"""
        LOAD CSV WITH HEADERS FROM '{filepath}' AS row
        MERGE (p:Person {{id: toInteger(row.PersonId)}})
        MERGE (po:Post {{id: toInteger(row.PostId)}})
        """
        try:
            tx.run(query)
            logger.info(f"Created Person-Post nodes from: {filepath}")
        except Exception as e:
            logger.error(f"Error creating Person-Post nodes from {filepath}: {str(e)}")

    def create_person_likes_comment_nodes(self, tx, filepath):
        query = f"""
        LOAD CSV WITH HEADERS FROM '{filepath}' AS row
        MERGE (p:Person {{id: toInteger(row.PersonId)}})
        MERGE (c:Comment {{id: toInteger(row.CommentId)}})
        """
        try:
            tx.run(query)
            logger.info(f"Created Person-Comment nodes from: {filepath}")
        except Exception as e:
            logger.error(f"Error creating Person-Comment nodes from {filepath}: {str(e)}")

    def create_person_has_interest_tag_nodes(self, tx, filepath):
        query = f"""
        LOAD CSV WITH HEADERS FROM '{filepath}' AS row
        MERGE (p:Person {{id: toInteger(row.PersonId)}})
        MERGE (t:Tag {{id: toInteger(row.TagId)}})
        """
        try:
            tx.run(query)
            logger.info(f"Created Person-Tag nodes from: {filepath}")
        except Exception as e:
            logger.error(f"Error creating Person-Tag nodes from {filepath}: {str(e)}")

    def create_forum_has_member_person_nodes(self, tx, filepath):
        query = f"""
        LOAD CSV WITH HEADERS FROM '{filepath}' AS row
        MERGE (f:Forum {{id: toInteger(row.ForumId)}})
        MERGE (p:Person {{id: toInteger(row.PersonId)}})
        """
        try:
            tx.run(query)
            logger.info(f"Created Forum-Person nodes from: {filepath}")
        except Exception as e:
            logger.error(f"Error creating Forum-Person nodes from {filepath}: {str(e)}")

    def create_forum_has_tag_tag_nodes(self, tx, filepath):
        query = f"""
        LOAD CSV WITH HEADERS FROM '{filepath}' AS row
        MERGE (f:Forum {{id: toInteger(row.ForumId)}})
        MERGE (t:Tag {{id: toInteger(row.TagId)}})
        """
        try:
            tx.run(query)
            logger.info(f"Created Forum-Tag nodes from: {filepath}")
        except Exception as e:
            logger.error(f"Error creating Forum-Tag nodes from {filepath}: {str(e)}")

    def create_post_has_tag_tag_nodes(self, tx, filepath):
        query = f"""
        LOAD CSV WITH HEADERS FROM '{filepath}' AS row
        MERGE (p:Post {{id: toInteger(row.PostId)}})
        MERGE (t:Tag {{id: toInteger(row.TagId)}})
        """
        try:
            tx.run(query)
            logger.info(f"Created Post-Tag nodes from: {filepath}")
        except Exception as e:
            logger.error(f"Error creating Post-Tag nodes from {filepath}: {str(e)}")

    def create_comment_has_tag_tag_nodes(self, tx, filepath):
        query = f"""
        LOAD CSV WITH HEADERS FROM '{filepath}' AS row
        MERGE (c:Comment {{id: toInteger(row.CommentId)}})
        MERGE (t:Tag {{id: toInteger(row.TagId)}})
        """
        try:
            tx.run(query)
            logger.info(f"Created Comment-Tag nodes from: {filepath}")
        except Exception as e:
            logger.error(f"Error creating Comment-Tag nodes from {filepath}: {str(e)}")

    def create_person_study_at_university_nodes(self, tx, filepath):
        query = f"""
        LOAD CSV WITH HEADERS FROM '{filepath}' AS row
        MERGE (p:Person {{id: toInteger(row.PersonId)}})
        MERGE (u:University {{id: toInteger(row.UniversityId)}})
        """
        try:
            tx.run(query)
            logger.info(f"Created Person-University nodes from: {filepath}")
        except Exception as e:
            logger.error(f"Error creating Person-University nodes from {filepath}: {str(e)}")

    def create_person_work_at_company_nodes(self, tx, filepath):
        query = f"""
        LOAD CSV WITH HEADERS FROM '{filepath}' AS row
        MERGE (p:Person {{id: toInteger(row.PersonId)}})
        MERGE (c:Company {{id: toInteger(row.CompanyId)}})
        """
        try:
            tx.run(query)
            logger.info(f"Created Person-Company nodes from: {filepath}")
        except Exception as e:
            logger.error(f"Error creating Person-Company nodes from {filepath}: {str(e)}")

    # Relationship import methods from your original code
    def import_knows_relationships(self, tx, filepath):
        query = f"""
        LOAD CSV WITH HEADERS FROM '{filepath}' AS row
        MATCH (p1:Person {{id: toInteger(row.Person1Id)}})
        MATCH (p2:Person {{id: toInteger(row.Person2Id)}})
        CREATE (p1)-[:KNOWS {{creationDate: row.creationDate}}]->(p2)
        """
        try:
            tx.run(query)
            logger.info(f"Imported KNOWS relationships from: {filepath}")
        except Exception as e:
            logger.error(f"Error importing KNOWS from {filepath}: {str(e)}")

    def import_likes_post_relationships(self, tx, filepath):
        query = f"""
        LOAD CSV WITH HEADERS FROM '{filepath}' AS row
        MATCH (p:Person {{id: toInteger(row.PersonId)}})
        MATCH (post:Post {{id: toInteger(row.PostId)}})
        CREATE (p)-[:LIKES {{creationDate: row.creationDate}}]->(post)
        """
        try:
            tx.run(query)
            logger.info(f"Imported LIKES_POST relationships from: {filepath}")
        except Exception as e:
            logger.error(f"Error importing LIKES_POST from {filepath}: {str(e)}")

    def import_likes_comment_relationships(self, tx, filepath):
        query = f"""
        LOAD CSV WITH HEADERS FROM '{filepath}' AS row
        MATCH (p:Person {{id: toInteger(row.PersonId)}})
        MATCH (c:Comment {{id: toInteger(row.CommentId)}})
        CREATE (p)-[:LIKES {{creationDate: row.creationDate}}]->(c)
        """
        try:
            tx.run(query)
            logger.info(f"Imported LIKES_COMMENT relationships from: {filepath}")
        except Exception as e:
            logger.error(f"Error importing LIKES_COMMENT from {filepath}: {str(e)}")

    def import_has_interest_relationships(self, tx, filepath):
        query = f"""
        LOAD CSV WITH HEADERS FROM '{filepath}' AS row
        MATCH (p:Person {{id: toInteger(row.PersonId)}})
        MATCH (t:Tag {{id: toInteger(row.TagId)}})
        CREATE (p)-[:HAS_INTEREST {{creationDate: row.creationDate}}]->(t)
        """
        try:
            tx.run(query)
            logger.info(f"Imported HAS_INTEREST relationships from: {filepath}")
        except Exception as e:
            logger.error(f"Error importing HAS_INTEREST from {filepath}: {str(e)}")

    def import_forum_member_relationships(self, tx, filepath):
        query = f"""
        LOAD CSV WITH HEADERS FROM '{filepath}' AS row
        MATCH (f:Forum {{id: toInteger(row.ForumId)}})
        MATCH (p:Person {{id: toInteger(row.PersonId)}})
        CREATE (f)-[:HAS_MEMBER {{joinDate: row.joinDate}}]->(p)
        """
        try:
            tx.run(query)
            logger.info(f"Imported FORUM_MEMBER relationships from: {filepath}")
        except Exception as e:
            logger.error(f"Error importing FORUM_MEMBER from {filepath}: {str(e)}")

    def import_forum_has_tag_relationships(self, tx, filepath):
        query = f"""
        LOAD CSV WITH HEADERS FROM '{filepath}' AS row
        MATCH (f:Forum {{id: toInteger(row.ForumId)}})
        MATCH (t:Tag {{id: toInteger(row.TagId)}})
        CREATE (f)-[:HAS_TAG]->(t)
        """
        try:
            tx.run(query)
            logger.info(f"Imported FORUM_HAS_TAG relationships from: {filepath}")
        except Exception as e:
            logger.error(f"Error importing FORUM_HAS_TAG from {filepath}: {str(e)}")

    def import_post_has_tag_relationships(self, tx, filepath):
        query = f"""
        LOAD CSV WITH HEADERS FROM '{filepath}' AS row
        MATCH (p:Post {{id: toInteger(row.PostId)}})
        MATCH (t:Tag {{id: toInteger(row.TagId)}})
        CREATE (p)-[:HAS_TAG]->(t)
        """
        try:
            tx.run(query)
            logger.info(f"Imported POST_HAS_TAG relationships from: {filepath}")
        except Exception as e:
            logger.error(f"Error importing POST_HAS_TAG from {filepath}: {str(e)}")

    def import_comment_has_tag_relationships(self, tx, filepath):
        query = f"""
        LOAD CSV WITH HEADERS FROM '{filepath}' AS row
        MATCH (c:Comment {{id: toInteger(row.CommentId)}})
        MATCH (t:Tag {{id: toInteger(row.TagId)}})
        CREATE (c)-[:HAS_TAG]->(t)
        """
        try:
            tx.run(query)
            logger.info(f"Imported COMMENT_HAS_TAG relationships from: {filepath}")
        except Exception as e:
            logger.error(f"Error importing COMMENT_HAS_TAG from {filepath}: {str(e)}")

    def import_study_at_relationships(self, tx, filepath):
        query = f"""
        LOAD CSV WITH HEADERS FROM '{filepath}' AS row
        MATCH (p:Person {{id: toInteger(row.PersonId)}})
        MATCH (u:University {{id: toInteger(row.UniversityId)}})
        CREATE (p)-[:STUDIES_AT {{classYear: toInteger(row.classYear)}}]->(u)
        """
        try:
            tx.run(query)
            logger.info(f"Imported STUDY_AT relationships from: {filepath}")
        except Exception as e:
            logger.error(f"Error importing STUDY_AT from {filepath}: {str(e)}")

    def import_work_at_relationships(self, tx, filepath):
        query = f"""
        LOAD CSV WITH HEADERS FROM '{filepath}' AS row
        MATCH (p:Person {{id: toInteger(row.PersonId)}})
        MATCH (c:Company {{id: toInteger(row.CompanyId)}})
        CREATE (p)-[:WORKS_AT {{workFrom: toInteger(row.workFrom)}}]->(c)
        """
        try:
            tx.run(query)
            logger.info(f"Imported WORK_AT relationships from: {filepath}")
        except Exception as e:
            logger.error(f"Error importing WORK_AT from {filepath}: {str(e)}")

    def import_nodes(self, knows_files, likes_post_files, likes_comment_files, has_interest_files,
                     member_of_files, forum_has_tag_files, post_has_tag_files, comment_has_tag_files,
                     study_at_files, work_at_files):
        with self.driver.session() as session:
            tx = session.begin_transaction()

            try:
                # KNOWS
                logger.info("Creating Person nodes from KNOWS files...")
                for file in knows_files:
                    filepath = f"file:///{file}"
                    self.create_person_knows_person_nodes(tx, filepath)
                logger.info("Finished creating Person nodes from KNOWS.")

                # LIKES_POST
                logger.info("Creating Person and Post nodes from LIKES_POST files...")
                for file in likes_post_files:
                    filepath = f"file:///{file}"
                    self.create_person_likes_post_nodes(tx, filepath)
                logger.info("Finished creating Person and Post nodes from LIKES_POST.")

                # LIKES_COMMENT
                logger.info("Creating Person and Comment nodes from LIKES_COMMENT files...")
                for file in likes_comment_files:
                    filepath = f"file:///{file}"
                    self.create_person_likes_comment_nodes(tx, filepath)
                logger.info("Finished creating Person and Comment nodes from LIKES_COMMENT.")

                # HAS_INTEREST
                logger.info("Creating Person and Tag nodes from HAS_INTEREST files...")
                for file in has_interest_files:
                    filepath = f"file:///{file}"
                    self.create_person_has_interest_tag_nodes(tx, filepath)
                logger.info("Finished creating Person and Tag nodes from HAS_INTEREST.")

                # MEMBER_OF
                logger.info("Creating Forum and Person nodes from MEMBER_OF files...")
                for file in member_of_files:
                    filepath = f"file:///{file}"
                    self.create_forum_has_member_person_nodes(tx, filepath)
                logger.info("Finished creating Forum and Person nodes from MEMBER_OF.")

                # FORUM_HAS_TAG
                logger.info("Creating Forum and Tag nodes from FORUM_HAS_TAG files...")
                for file in forum_has_tag_files:
                    filepath = f"file:///{file}"
                    self.create_forum_has_tag_tag_nodes(tx, filepath)
                logger.info("Finished creating Forum and Tag nodes from FORUM_HAS_TAG.")

                # POST_HAS_TAG
                logger.info("Creating Post and Tag nodes from POST_HAS_TAG files...")
                for file in post_has_tag_files:
                    filepath = f"file:///{file}"
                    self.create_post_has_tag_tag_nodes(tx, filepath)
                logger.info("Finished creating Post and Tag nodes from POST_HAS_TAG.")

                # COMMENT_HAS_TAG
                logger.info("Creating Comment and Tag nodes from COMMENT_HAS_TAG files...")
                for file in comment_has_tag_files:
                    filepath = f"file:///{file}"
                    self.create_comment_has_tag_tag_nodes(tx, filepath)
                logger.info("Finished creating Comment and Tag nodes from COMMENT_HAS_TAG.")

                # STUDY_AT
                logger.info("Creating Person and University nodes from STUDY_AT files...")
                for file in study_at_files:
                    filepath = f"file:///{file}"
                    self.create_person_study_at_university_nodes(tx, filepath)
                logger.info("Finished creating Person and University nodes from STUDY_AT.")

                # WORK_AT
                logger.info("Creating Person and Company nodes from WORK_AT files...")
                for file in work_at_files:
                    filepath = f"file:///{file}"
                    self.create_person_work_at_company_nodes(tx, filepath)
                logger.info("Finished creating Person and Company nodes from WORK_AT.")

                tx.commit()
                logger.info("All node creation operations completed successfully.")

            except Exception as e:
                tx.rollback()
                logger.error(f"Error during node creation: {str(e)}")

    # def run_import(self, knows_files, likes_post_files, likes_comment_files, has_interest_files,
    #                member_of_files, forum_has_tag_files, post_has_tag_files, comment_has_tag_files,
    #                study_at_files, work_at_files):
    #     with self.driver.session() as session:
    #         tx = session.begin_transaction()
    #
    #         try:
    #             # KNOWS
    #             logger.info("Starting import of KNOWS relationships...")
    #             for file in knows_files:
    #                 filepath = f"file:///{file}"
    #                 self.import_knows_relationships(tx, filepath)
    #             logger.info("Finished import of KNOWS relationships.")
    #
    #             # LIKES_POST
    #             logger.info("Starting import of LIKES_POST relationships...")
    #             for file in likes_post_files:
    #                 filepath = f"file:///{file}"
    #                 self.import_likes_post_relationships(tx, filepath)
    #             logger.info("Finished import of LIKES_POST relationships.")
    #
    #             # LIKES_COMMENT
    #             logger.info("Starting import of LIKES_COMMENT relationships...")
    #             for file in likes_comment_files:
    #                 filepath = f"file:///{file}"
    #                 self.import_likes_comment_relationships(tx, filepath)
    #             logger.info("Finished import of LIKES_COMMENT relationships.")
    #
    #             # HAS_INTEREST
    #             logger.info("Starting import of HAS_INTEREST relationships...")
    #             for file in has_interest_files:
    #                 filepath = f"file:///{file}"
    #                 self.import_has_interest_relationships(tx, filepath)
    #             logger.info("Finished import of HAS_INTEREST relationships.")
    #
    #             # FORUM_MEMBER
    #             logger.info("Starting import of FORUM_MEMBER relationships...")
    #             for file in member_of_files:
    #                 filepath = f"file:///{file}"
    #                 self.import_forum_member_relationships(tx, filepath)
    #             logger.info("Finished import of FORUM_MEMBER relationships.")
    #
    #             # FORUM_HAS_TAG
    #             logger.info("Starting import of FORUM_HAS_TAG relationships...")
    #             for file in forum_has_tag_files:
    #                 filepath = f"file:///{file}"
    #                 self.import_forum_has_tag_relationships(tx, filepath)
    #             logger.info("Finished import of FORUM_HAS_TAG relationships.")
    #
    #             # POST_HAS_TAG
    #             logger.info("Starting import of POST_HAS_TAG relationships...")
    #             for file in post_has_tag_files:
    #                 filepath = f"file:///{file}"
    #                 self.import_post_has_tag_relationships(tx, filepath)
    #             logger.info("Finished import of POST_HAS_TAG relationships.")
    #
    #             # COMMENT_HAS_TAG
    #             logger.info("Starting import of COMMENT_HAS_TAG relationships...")
    #             for file in comment_has_tag_files:
    #                 filepath = f"file:///{file}"
    #                 self.import_comment_has_tag_relationships(tx, filepath)
    #             logger.info("Finished import of COMMENT_HAS_TAG relationships.")
    #
    #             # STUDY_AT
    #             logger.info("Starting import of STUDY_AT relationships...")
    #             for file in study_at_files:
    #                 filepath = f"file:///{file}"
    #                 self.import_study_at_relationships(tx, filepath)
    #             logger.info("Finished import of STUDY_AT relationships.")
    #
    #             # WORK_AT
    #             logger.info("Starting import of WORK_AT relationships...")
    #             for file in work_at_files:
    #                 filepath = f"file:///{file}"
    #                 self.import_work_at_relationships(tx, filepath)
    #             logger.info("Finished import of WORK_AT relationships.")
    #
    #             tx.commit()
    #             logger.info("All relationship imports completed successfully.")
    #
    #         except Exception as e:
    #             tx.rollback()
    #             logger.error(f"Error during relationship import: {str(e)}")

    def run_import(self, knows_files, likes_post_files, likes_comment_files, has_interest_files,
                   member_of_files, forum_has_tag_files, post_has_tag_files, comment_has_tag_files,
                   study_at_files, work_at_files):
        with self.driver.session() as session:
            tx = session.begin_transaction()

            try:
                # Import KNOWS relationships
                logger.info("Starting import of KNOWS relationships...")
                for file in knows_files:
                    filepath = f"file:///{file}"  # Notice the triple slash (instead of 4 slashes)
                    self.import_knows_relationships(tx, filepath)
                logger.info("Finished import of KNOWS relationships.")

                # Import LIKES_POST relationships
                logger.info("Starting import of LIKES_POST relationships...")
                for file in likes_post_files:
                    filepath = f"file:///{file}"
                    self.import_likes_post_relationships(tx, filepath)
                logger.info("Finished import of LIKES_POST relationships.")

                # Import LIKES_COMMENT relationships
                logger.info("Starting import of LIKES_COMMENT relationships...")
                for file in likes_comment_files:
                    filepath = f"file:///{file}"
                    self.import_likes_comment_relationships(tx, filepath)
                logger.info("Finished import of LIKES_COMMENT relationships.")

                # Import HAS_INTEREST relationships
                logger.info("Starting import of HAS_INTEREST relationships...")
                for file in has_interest_files:
                    filepath = f"file:///{file}"
                    self.import_has_interest_relationships(tx, filepath)
                logger.info("Finished import of HAS_INTEREST relationships.")

                # Import FORUM_MEMBER relationships
                logger.info("Starting import of FORUM_MEMBER relationships...")
                for file in member_of_files:
                    filepath = f"file:///{file}"
                    self.import_forum_member_relationships(tx, filepath)
                logger.info("Finished import of FORUM_MEMBER relationships.")

                # Import FORUM_HAS_TAG relationships
                logger.info("Starting import of FORUM_HAS_TAG relationships...")
                for file in forum_has_tag_files:
                    filepath = f"file:///{file}"
                    self.import_forum_has_tag_relationships(tx, filepath)
                logger.info("Finished import of FORUM_HAS_TAG relationships.")

                # Import POST_HAS_TAG relationships
                logger.info("Starting import of POST_HAS_TAG relationships...")
                for file in post_has_tag_files:
                    filepath = f"file:///{file}"
                    self.import_post_has_tag_relationships(tx, filepath)
                logger.info("Finished import of POST_HAS_TAG relationships.")

                # Import COMMENT_HAS_TAG relationships
                logger.info("Starting import of COMMENT_HAS_TAG relationships...")
                for file in comment_has_tag_files:
                    filepath = f"file:///{file}"
                    self.import_comment_has_tag_relationships(tx, filepath)
                logger.info("Finished import of COMMENT_HAS_TAG relationships.")

                # Import STUDY_AT relationships
                logger.info("Starting import of STUDY_AT relationships...")
                for file in study_at_files:
                    filepath = f"file:///{file}"
                    self.import_study_at_relationships(tx, filepath)
                logger.info("Finished import of STUDY_AT relationships.")

                # Import WORK_AT relationships
                logger.info("Starting import of WORK_AT relationships...")
                for file in work_at_files:
                    filepath = f"file:///{file}"
                    self.import_work_at_relationships(tx, filepath)
                logger.info("Finished import of WORK_AT relationships.")

                # Commit the transaction
                tx.commit()
                logger.info("All relationships imported successfully.")

            except Exception as e:
                tx.rollback()
                logger.error(f"Error during import: {str(e)}")


def initialize_database():
    logger.info("Initializing database...")
    logger.info("Neo4j initialization starting...")

    # Load environment variables from .env file
    load_dotenv()

    # Configure these values using .env variables
    uri = os.getenv("NEO4J_URI")
    user = os.getenv("NEO4J_USER")
    password = os.getenv("NEO4J_PASSWORD")

    importer = Neo4jImporter(uri, user, password)

    try:
        # Create constraints
        importer.create_constraints()

        # First import all nodes
        logger.info("=== Creating nodes ===")

        # Define relationship file paths arrays
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

        # Then import relationships
        logger.info("=== Creating relationships ===")
        importer.import_nodes(knows_files, likes_post_files, likes_comment_files, has_interest_files,
                              member_of_files, forum_has_tag_files, post_has_tag_files, comment_has_tag_files,
                              study_at_files, work_at_files)

        importer.run_import(
            knows_files, likes_post_files, likes_comment_files, has_interest_files,
            member_of_files, forum_has_tag_files, post_has_tag_files, comment_has_tag_files,
            study_at_files, work_at_files
        )

        logger.info("Neo4j initialization finished...")
    except Exception as e:
        logger.error(f"Error during Neo4j initialization: {str(e)}")
    finally:
        importer.close()


if __name__ == "__main__":
    initialize_database()
    logger.info("#### Database initialization complete. ####")
