from neo4j import GraphDatabase
from config import settings

driver = GraphDatabase.driver(
    settings.neo4j_uri,
    auth=(settings.neo4j_user, settings.neo4j_password)
)


def get_friends_of(name: str) -> list[str]:
    with driver.session() as session:
        result = session.run(
            """
            MATCH (p:Person {name: $name})-[:KNOWS]->(friend)
            RETURN friend.name AS name
            """,
            name=name
        )
        return [record["name"] for record in result]
