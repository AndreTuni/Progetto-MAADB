from pymongo import MongoClient, InsertOne
import os
import pandas as pd
import psycopg
from psycopg.sql import SQL, Identifier
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()





def load_large_csvs_to_mongodb(collection_name, csv_paths, id_field="id", chunksize=10000):
    """Loads large CSV files into a MongoDB collection, skipping existing documents."""
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
    """Initializes MongoDB database by loading data from CSV files."""
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
load_mongodb()