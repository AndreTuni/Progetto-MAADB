from pymongo import MongoClient, InsertOne
import os
import pandas as pd
import psycopg
from psycopg.sql import SQL, Identifier
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


def load_large_csvs_to_postgres(table_name, csv_paths, id_column, connection, chunksize=1000):
    cursor = connection.cursor()
    for csv_path in csv_paths:
        print(f"Loading {csv_path} into {table_name}...")
        for chunk in pd.read_csv(csv_path, sep="|", chunksize=chunksize):
            chunk.drop_duplicates(subset=[id_column], inplace=True)
            rows = [tuple(row) for index, row in chunk.iterrows()]
            if rows:
                columns = list(chunk.columns)
                placeholders = SQL(', ').join(SQL('%s') * len(columns))
                insert_sql = SQL('INSERT INTO {} ({}) VALUES {} ON CONFLICT ({}) DO NOTHING').format(
                    Identifier(table_name),
                    SQL(', ').join(Identifier(col) for col in columns),
                    SQL(', ').join(SQL('({})').format(placeholders) for _ in rows),
                    Identifier(id_column)
                )
                cursor.execute(insert_sql, [val for row in rows for val in row])
        connection.commit()
        print(f"Finished loading {csv_path} into {table_name}.")


def load_postgres():
    print("Initializing PostgreSQL from CSV...")

    # Retrieve PostgreSQL connection info from environment variables
    conn = psycopg.connect(
        dbname=os.getenv("POSTGRES_DB", "maadb"),
        user=os.getenv("POSTGRES_USER", "postgres"),
        password=os.getenv("POSTGRES_PASSWORD", "password"),
        host=os.getenv("POSTGRES_HOST", "localhost"),
        port=os.getenv("POSTGRES_PORT", "5432")
    )
    cursor = conn.cursor()

    # Define SQL commands to CREATE TABLES (adjust these based on your schema)
    create_organisation_table = """
    CREATE TABLE IF NOT EXISTS organization (
        id TEXT PRIMARY KEY,
        type TEXT,
        name TEXT,
        url TEXT,
        location TEXT
        -- Add other columns as needed
    );
    """

    create_place_table = """
    CREATE TABLE IF NOT EXISTS place (
        id TEXT PRIMARY KEY,
        name TEXT,
        url TEXT,
        type TEXT,
        latitude FLOAT,
        longitude FLOAT,
        isPartOf TEXT
        -- Add other columns as needed
    );
    """

    create_tag_table = """
    CREATE TABLE IF NOT EXISTS tag (
        id TEXT PRIMARY KEY,
        name TEXT,
        url TEXT
        -- Add other columns as needed
    );
    """

    create_tagclass_table = """
    CREATE TABLE IF NOT EXISTS tagclass (
        id TEXT PRIMARY KEY,
        name TEXT,
        url TEXT,
        subClassOf TEXT
        -- Add other columns as needed
    );
    """

    # Execute the CREATE TABLE commands
    cursor.execute(create_organisation_table)
    cursor.execute(create_place_table)
    cursor.execute(create_tag_table)
    cursor.execute(create_tagclass_table)
    conn.commit()
    print("PostgreSQL tables created.")

    # Now load the data
    org_files = ["/app/data/static/Organisation/part-00000-1b7378fc-ddc5-45ae-a217-23037b649081-c000.csv"]
    place_files = ["/app/data/static/Place/part-00000-5d3b389c-4734-4de7-a476-66a0fe967afc-c000.csv"]
    tag_files = ["/app/data/static/Tag/part-00000-4bdec47c-71f2-4e9a-9b75-2a8f7b011870-c000.csv"]
    tagclass_files = ["/app/data/static/TagClass/part-00000-4dea37c1-863e-4d43-adfe-95d3ae0a86a9-c000.csv"]

    load_large_csvs_to_postgres("organization", org_files, "id", conn)
    load_large_csvs_to_postgres("place", place_files, "id", conn)
    load_large_csvs_to_postgres("tag", tag_files, "id", conn)
    load_large_csvs_to_postgres("tagclass", tagclass_files, "id", conn)

    conn.close()
    print("PostgreSQL import complete.")


def load_large_csvs_to_mongodb(collection_name, csv_paths, id_field="id", chunksize=10000):
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/maadb")
    client = MongoClient(mongodb_uri)
    db = client.get_database()
    collection = db[collection_name]
    existing_ids = set(collection.distinct(id_field))

    for csv_path in csv_paths:
        print(f"Loading {csv_path} into {collection_name}...")
        for chunk in pd.read_csv(csv_path, sep="|", chunksize=chunksize):
            chunk = chunk[~chunk[id_field].isin(existing_ids)]
            if not chunk.empty:
                requests = [InsertOne(row) for row in chunk.to_dict(orient="records")]
                collection.bulk_write(requests)
            existing_ids.update(chunk[id_field].tolist())

    print(f"{collection_name} collection updated successfully.")


def load_mongodb():
    print("Initializing MongoDB from CSV...")

    # Replace these with lists of actual absolute paths for each entity
    person_files = [
        "app/data/dynamic/Person/part-00000-dd2f2cde-5db9-4c99-ae95-2edc4a618386-c000.csv",
        "app/data/dynamic/Person/part-00001-dd2f2cde-5db9-4c99-ae95-2edc4a618386-c000.csv",
        "app/data/dynamic/Person/part-00002-dd2f2cde-5db9-4c99-ae95-2edc4a618386-c000.csv"
    ]
    post_files = [
        "app/data/dynamic/Post/part-00000-b97b8177-f70d-47ee-9a1f-2a70ca3f97c4-c000.csv",
        "app/data/dynamic/Post/part-00001-b97b8177-f70d-47ee-9a1f-2a70ca3f97c4-c000.csv",
        "app/data/dynamic/Post/part-00003-b97b8177-f70d-47ee-9a1f-2a70ca3f97c4-c000.csv",
        "app/data/dynamic/Post/part-00006-b97b8177-f70d-47ee-9a1f-2a70ca3f97c4-c000.csv"
    ]
    comment_files = [
        "app/data/dynamic/Comment/part-00000-833bf12c-c29e-47ce-b45b-08899b08abd3-c000.csv",
        "app/data/dynamic/Comment/part-00006-833bf12c-c29e-47ce-b45b-08899b08abd3-c000.csv",
        "app/data/dynamic/Comment/part-00005-833bf12c-c29e-47ce-b45b-08899b08abd3-c000.csv",
        "app/data/dynamic/Comment/part-00003-833bf12c-c29e-47ce-b45b-08899b08abd3-c000.csv",
        "app/data/dynamic/Comment/part-00001-833bf12c-c29e-47ce-b45b-08899b08abd3-c000.csv",
        "app/data/dynamic/Comment/part-00004-833bf12c-c29e-47ce-b45b-08899b08abd3-c000.csv",
        "app/data/dynamic/Comment/part-00008-833bf12c-c29e-47ce-b45b-08899b08abd3-c000.csv",
        "app/data/dynamic/Comment/part-00007-833bf12c-c29e-47ce-b45b-08899b08abd3-c000.csv",
        "app/data/dynamic/Comment/part-00002-833bf12c-c29e-47ce-b45b-08899b08abd3-c000.csv"
    ]
    forum_files = [
        "app/data/dynamic/Forum/part-00000-a997c396-dbaf-4755-b9d6-7f3d6066961a-c000.csv",
        "app/data/dynamic/Forum/part-00001-a997c396-dbaf-4755-b9d6-7f3d6066961a-c000.csv",
        "app/data/dynamic/Forum/part-00002-a997c396-dbaf-4755-b9d6-7f3d6066961a-c000.csv"
        ]


    load_large_csvs_to_mongodb("person", person_files)
    load_large_csvs_to_mongodb("post", post_files)
    load_large_csvs_to_mongodb("comment", comment_files)
    load_large_csvs_to_mongodb("forum", forum_files)

    print("MongoDB import complete.")

# Call the functions to load data
load_postgres()
load_mongodb()