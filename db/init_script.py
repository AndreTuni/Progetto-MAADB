"""
Database initialization script.
Run this once to set up your databases with initial schema and data.
"""
import os
import sys
import time
from pathlib import Path

# Add the parent directory to path so we can import modules
sys.path.append(str(Path(__file__).parent.parent))

# Wait for databases to be ready
print("Waiting for databases to be ready...")
time.sleep(5)

# Initialize PostgreSQL
print("Initializing PostgreSQL...")
try:
    from sqlalchemy import create_engine, Column, Integer, String, MetaData, Table, text

    # Get PostgreSQL connection details from environment variables
    postgres_user = os.environ.get("POSTGRES_USER", "postgres")
    postgres_password = os.environ.get("POSTGRES_PASSWORD", "password")
    postgres_host = os.environ.get("POSTGRES_HOST", "localhost")
    postgres_db = os.environ.get("POSTGRES_DB", "university_project")

    connection_string = f"postgresql://{postgres_user}:{postgres_password}@{postgres_host}/{postgres_db}"
    engine = create_engine(connection_string)

    # Create tables
    metadata = MetaData()

    # Example table
    users = Table(
        'users',
        metadata,
        Column('id', Integer, primary_key=True),
        Column('name', String(50)),
        Column('email', String(100))
    )

    # Create all tables
    metadata.create_all(engine)

    # Insert sample data
    with engine.connect() as conn:
        conn.execute(
            text("INSERT INTO users (name, email) VALUES (:name, :email)"),
            [
                {"name": "Alice", "email": "alice@example.com"},
                {"name": "Bob", "email": "bob@example.com"},
                {"name": "Charlie", "email": "charlie@example.com"}
            ]
        )
        conn.commit()

    print("PostgreSQL initialized successfully!")
except Exception as e:
    print(f"Error initializing PostgreSQL: {e}")

# Initialize MongoDB
print("Initializing MongoDB...")
try:
    from pymongo import MongoClient

    # Get MongoDB connection details from environment variables
    mongodb_uri = os.environ.get("MONGODB_URI", "mongodb://localhost:27017/university_project")

    client = MongoClient(mongodb_uri)
    db = client.get_database()

    # Create collections and insert sample data
    products_collection = db.products
    products_collection.insert_many([
        {"name": "Laptop", "price": 999.99, "category": "Electronics"},
        {"name": "Smartphone", "price": 699.99, "category": "Electronics"},
        {"name": "Headphones", "price": 149.99, "category": "Accessories"}
    ])

    print("MongoDB initialized successfully!")
except Exception as e:
    print(f"Error initializing MongoDB: {e}")

# Initialize Neo4j
print("Initializing Neo4j...")
try:
    from neo4j import GraphDatabase

    # Get Neo4j connection details from environment variables
    neo4j_uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "password")

    driver = GraphDatabase.driver(neo4j_uri, auth=(neo4j_user, neo4j_password))

    # Create nodes and relationships
    with driver.session() as session:
        # Create some nodes and relationships
        session.run("""
        CREATE (alice:Person {name: 'Alice', age: 30})
        CREATE (bob:Person {name: 'Bob', age: 35})
        CREATE (charlie:Person {name: 'Charlie', age: 25})
        CREATE (datascience:Project {name: 'Data Science'})
        CREATE (webdev:Project {name: 'Web Development'})
        CREATE (alice)-[:WORKS_ON]->(datascience)
        CREATE (bob)-[:WORKS_ON]->(datascience)
        CREATE (bob)-[:WORKS_ON]->(webdev)
        CREATE (charlie)-[:WORKS_ON]->(webdev)
        """)

    print("Neo4j initialized successfully!")
except Exception as e:
    print(f"Error initializing Neo4j: {e}")

print("Database initialization complete!")