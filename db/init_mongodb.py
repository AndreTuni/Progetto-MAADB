# from pymongo import MongoClient, InsertOne, ASCENDING
# import os
# import pandas as pd
# from dotenv import load_dotenv
#
# # Load environment variables from .env file
# load_dotenv()
#
#
# def get_mongo_client():
#     mongodb_uri = os.getenv("MONGODB_URI", "mongodb://mongodb:27017/maadb")
#     print(f"Connecting to MongoDB URI: {mongodb_uri}")  # Added print statement
#     client = MongoClient(
#         mongodb_uri,
#         connectTimeoutMS=120000,  # 120 seconds connection timeout
#         socketTimeoutMS=180000  # 180 seconds socket (read/write) timeout
#     )
#     print("MongoDB client initialized.")  # Added print statement
#     return client
#
#
# def load_large_csvs_to_mongodb(collection_name, csv_paths, id_field="id", chunksize=10000):
#     """Loads large CSV files into a MongoDB collection, skipping existing documents."""
#     client = get_mongo_client()
#     db = client.get_database()
#     collection = db[collection_name]
#     print(f"######################################################################")
#     print(f"################# STARTING LOAD INTO: {collection_name.upper()} #################")
#     print(f"######################################################################")
#
#     try:
#         # Initialize the set of existing IDs using a generator to avoid loading them all at once
#         existing_ids = set()
#         print(f"Fetching existing IDs for {collection_name}...")  # Added print statement
#         cursor = collection.find({}, {id_field: 1})  # Fetch only the id_field
#
#         # Use the cursor to add IDs to the set
#         count_existing = 0
#         for doc in cursor:
#             existing_ids.add(doc[id_field])
#             count_existing += 1
#         print(f"Found {count_existing} existing documents in {collection_name}.")  # Added print statement
#
#         # Now process the CSV files in chunks
#         for csv_path in csv_paths:
#             print(f"Loading {csv_path} into {collection_name}...")
#             chunk_number = 0
#             for chunk in pd.read_csv(csv_path, sep="|", chunksize=chunksize):
#                 chunk_number += 1
#                 # print(f"Processing chunk {chunk_number} with {len(chunk)} rows from {csv_path}...")  # Added print statement
#                 chunk = chunk[~chunk[id_field].isin(existing_ids)]
#
#                 if not chunk.empty:
#                     requests = [InsertOne(row) for row in chunk.to_dict(orient="records")]
#                     result = collection.bulk_write(requests)
#                     print(
#                         f"Inserted {result.inserted_count} new documents into {collection_name} from chunk {chunk_number} of {csv_path}.")  # Added print statement
#
#                 existing_ids.update(chunk[id_field].tolist())  # Update existing_ids with the IDs from this chunk
#             print(f"Finished loading {csv_path} into {collection_name}.")  # Added print statement
#     except Exception as e:
#         print(f"Error while processing {csv_path}: {e}")
#     finally:
#         client.close()
#
#     print(f"++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
#     print(f"+++++++ {collection_name.upper()} COLLECTION UPDATED SUCCESSFULLY +++++++")
#     print(f"++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
#
#
# def load_mongodb():
#     """Initializes MongoDB database by loading data from CSV files and creates indexes."""
#     print("Initializing MongoDB from CSV and creating indexes...")
#     client = get_mongo_client()
#     db = client.get_database()
#
#     try:
#         # Create indexes if they don't exist
#         print("Creating indexes...")
#         db.person.create_index([("id", ASCENDING)], name="person_id_index")
#         print("Created index for person collection.")  # Added print
#         db.post.create_index([("id", ASCENDING)], name="post_id_index")
#         print("Created index for post collection.")  # Added print
#         db.comment.create_index([("id", ASCENDING)], name="comment_id_index")
#         print("Created index for comment collection.")  # Added print
#         db.forum.create_index([("id", ASCENDING)], name="forum_id_index")
#         print("Created index for forum collection.")  # Added print
#         print("Indexes creation initiated.")  # Modified print
#
#         # Replace these with lists of actual absolute paths for each entity
#         person_files = [
#             "app/data/dynamic/Person/part-00000-dd2f2cde-5db9-4c99-ae95-2edc4a618386-c000.csv",
#             "app/data/dynamic/Person/part-00001-dd2f2cde-5db9-4c99-ae95-2edc4a618386-c000.csv",
#             "app/data/dynamic/Person/part-00002-dd2f2cde-5db9-4c99-ae95-2edc4a618386-c000.csv"
#         ]
#         post_files = [
#             "app/data/dynamic/Post/part-00000-b97b8177-f70d-47ee-9a1f-2a70ca3f97c4-c000.csv",
#             "app/data/dynamic/Post/part-00001-b97b8177-f70d-47ee-9a1f-2a70ca3f97c4-c000.csv",
#             "app/data/dynamic/Post/part-00003-b97b8177-f70d-47ee-9a1f-2a70ca3f97c4-c000.csv",
#             "app/data/dynamic/Post/part-00006-b97b8177-f70d-47ee-9a1f-2a70ca3f97c4-c000.csv"
#         ]
#         comment_files = [
#             "app/data/dynamic/Comment/part-00000-833bf12c-c29e-47ce-b45b-08899b08abd3-c000.csv",
#             "app/data/dynamic/Comment/part-00006-833bf12c-c29e-47ce-b45b-08899b08abd3-c000.csv",
#             "app/data/dynamic/Comment/part-00005-833bf12c-c29e-47ce-b45b-08899b08abd3-c000.csv",
#             "app/data/dynamic/Comment/part-00003-833bf12c-c29e-47ce-b45b-08899b08abd3-c000.csv",
#             "app/data/dynamic/Comment/part-00001-833bf12c-c29e-47ce-b45b-08899b08abd3-c000.csv",
#             "app/data/dynamic/Comment/part-00004-833bf12c-c29e-47ce-b45b-08899b08abd3-c000.csv",
#             "app/data/dynamic/Comment/part-00008-833bf12c-c29e-47ce-b45b-08899b08abd3-c000.csv",
#             "app/data/dynamic/Comment/part-00007-833bf12c-c29e-47ce-b45b-08899b08abd3-c000.csv",
#             "app/data/dynamic/Comment/part-00002-833bf12c-c29e-47ce-b45b-08899b08abd3-c000.csv"
#         ]
#         forum_files = [
#             "app/data/dynamic/Forum/part-00000-a997c396-dbaf-4755-b9d6-7f3d6066961a-c000.csv",
#             "app/data/dynamic/Forum/part-00001-a997c396-dbaf-4755-b9d6-7f3d6066961a-c000.csv",
#             "app/data/dynamic/Forum/part-00002-a997c396-dbaf-4755-b9d6-7f3d6066961a-c000.csv"
#         ]
#
#         load_large_csvs_to_mongodb("person", person_files)
#         load_large_csvs_to_mongodb("post", post_files)
#         load_large_csvs_to_mongodb("comment", comment_files)
#         load_large_csvs_to_mongodb("forum", forum_files)
#
#     finally:
#         if 'client' in locals() and client:
#             client.close()
#
#     print("MongoDB import complete.")
#
#
# # Call the functions to load data
# load_mongodb()


from pymongo import MongoClient, InsertOne, ASCENDING
import os
import pandas as pd
from dotenv import load_dotenv
import threading
import concurrent.futures
import time

# Load environment variables from .env file
load_dotenv()

# Global lock for thread-safe printing
print_lock = threading.Lock()


def thread_safe_print(*args, **kwargs):
    """Thread-safe printing function"""
    with print_lock:
        print(*args, **kwargs)


def get_mongo_client():
    mongodb_uri = os.getenv("MONGODB_URI", "mongodb://mongodb:27017/maadb")
    thread_safe_print(f"Connecting to MongoDB URI: {mongodb_uri}")
    client = MongoClient(
        mongodb_uri,
        connectTimeoutMS=120000,  # 120 seconds connection timeout
        socketTimeoutMS=180000  # 180 seconds socket (read/write) timeout
    )
    thread_safe_print("MongoDB client initialized.")
    return client


def load_csv_to_mongodb(collection_name, csv_path, id_field="id", chunksize=10000, existing_ids=None):
    """Loads a single CSV file into MongoDB, thread-safe version"""
    client = get_mongo_client()
    db = client.get_database()
    collection = db[collection_name]

    thread_safe_print(f"Starting to load {csv_path} into {collection_name}...")

    try:
        # Create a thread-local copy of existing_ids to avoid race conditions
        local_existing_ids = set(existing_ids) if existing_ids else set()

        # Process the CSV file in chunks
        chunk_number = 0
        total_inserted = 0

        for chunk in pd.read_csv(csv_path, sep="|", chunksize=chunksize):
            chunk_number += 1
            # Filter out records that already exist
            chunk = chunk[~chunk[id_field].isin(local_existing_ids)]

            if not chunk.empty:
                requests = [InsertOne(row) for row in chunk.to_dict(orient="records")]
                result = collection.bulk_write(requests)
                inserted_count = result.inserted_count
                total_inserted += inserted_count
                thread_safe_print(
                    f"Inserted {inserted_count} new documents into {collection_name} from chunk {chunk_number} of {csv_path}.")

                # Update local existing IDs set
                local_existing_ids.update(chunk[id_field].tolist())

        thread_safe_print(f"Finished loading {csv_path} into {collection_name}. Total inserted: {total_inserted}")
        return csv_path, total_inserted

    except Exception as e:
        thread_safe_print(f"Error while processing {csv_path}: {e}")
        return csv_path, 0
    finally:
        client.close()


def get_existing_ids(collection_name, id_field="id"):
    """Get existing IDs from a collection"""
    client = get_mongo_client()
    db = client.get_database()
    collection = db[collection_name]

    thread_safe_print(f"Fetching existing IDs for {collection_name}...")

    try:
        existing_ids = set()
        cursor = collection.find({}, {id_field: 1})

        count_existing = 0
        for doc in cursor:
            existing_ids.add(doc[id_field])
            count_existing += 1

        thread_safe_print(f"Found {count_existing} existing documents in {collection_name}.")
        return existing_ids

    finally:
        client.close()


def load_collection_with_threads(collection_name, csv_paths, id_field="id", max_workers=None):
    """Loads CSV files into a MongoDB collection using thread pool"""
    thread_safe_print(f"######################################################################")
    thread_safe_print(f"################# STARTING LOAD INTO: {collection_name.upper()} #################")
    thread_safe_print(f"######################################################################")

    start_time = time.time()

    # Get existing IDs once to avoid duplicate loading
    existing_ids = get_existing_ids(collection_name, id_field)

    # Use a thread pool to load files concurrently
    with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
        # Submit tasks for each CSV file
        future_to_csv = {
            executor.submit(
                load_csv_to_mongodb,
                collection_name,
                csv_path,
                id_field,
                10000,  # chunksize
                existing_ids
            ): csv_path for csv_path in csv_paths
        }

        # Process results as they complete
        total_inserted = 0
        for future in concurrent.futures.as_completed(future_to_csv):
            csv_path = future_to_csv[future]
            try:
                path, inserted = future.result()
                total_inserted += inserted
            except Exception as e:
                thread_safe_print(f"CSV {csv_path} generated an exception: {e}")

    end_time = time.time()
    duration = end_time - start_time

    thread_safe_print(f"++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
    thread_safe_print(f"+++++++ {collection_name.upper()} COLLECTION UPDATED SUCCESSFULLY +++++++")
    thread_safe_print(f"+++++++ Total inserted: {total_inserted}, Time: {duration:.2f} seconds +++++++")
    thread_safe_print(f"++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")


def create_indexes():
    """Create indexes for collections"""
    thread_safe_print("Creating indexes...")
    client = get_mongo_client()
    db = client.get_database()

    try:
        db.person.create_index([("id", ASCENDING)], name="person_id_index")
        thread_safe_print("Created index for person collection.")

        db.post.create_index([("id", ASCENDING)], name="post_id_index")
        thread_safe_print("Created index for post collection.")

        db.comment.create_index([("id", ASCENDING)], name="comment_id_index")
        thread_safe_print("Created index for comment collection.")

        db.forum.create_index([("id", ASCENDING)], name="forum_id_index")
        thread_safe_print("Created index for forum collection.")

        thread_safe_print("All indexes created successfully.")
    finally:
        client.close()


def load_mongodb(max_workers=None):
    """
    Initializes MongoDB database by loading data from CSV files and creates indexes.

    Args:
        max_workers: Maximum number of threads to use. If None, defaults to
                     min(32, os.cpu_count() + 4) as per ThreadPoolExecutor
    """
    thread_safe_print("Initializing MongoDB from CSV and creating indexes...")

    # Create indexes first
    create_indexes()

    # Define file paths for each collection
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

    # Load all collections - the heaviest operations are performed in parallel
    total_start_time = time.time()

    # You can adjust the order or use threading for collections too if needed
    load_collection_with_threads("person", person_files, max_workers=max_workers)
    load_collection_with_threads("post", post_files, max_workers=max_workers)
    load_collection_with_threads("comment", comment_files, max_workers=max_workers)
    load_collection_with_threads("forum", forum_files, max_workers=max_workers)

    total_end_time = time.time()
    total_duration = total_end_time - total_start_time

    thread_safe_print("MongoDB import complete.")
    thread_safe_print(f"Total execution time: {total_duration:.2f} seconds")


if __name__ == "__main__":
    # You can specify the number of workers to use, or let it use the default
    # For I/O bound tasks like this, using more workers than CPUs can be beneficial
    # A good rule of thumb is 2-3x the number of CPUs
    import os

    recommended_workers = min(32, (os.cpu_count() or 4) * 2)
    load_mongodb(max_workers=recommended_workers)