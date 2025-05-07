import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings  # Assumes config.py is in the same directory or accessible via PYTHONPATH


async def migrate_emails_to_array():
    """
    Migrates the 'email' field in the 'person' collection from a
    semicolon-separated string to an array of strings.
    """
    print(f"Connecting to MongoDB at: {settings.mongodb_uri}...")
    client = AsyncIOMotorClient(settings.mongodb_uri)
    # In your mongo_client.py, you use client.get_default_database().
    # Ensure the database name is part of mongodb_uri or is the default one.
    # If not, you might need to specify: db = client["your_db_name"]
    db = client.get_default_database()
    if not db.name:
        print(
            "Error: Could not determine database name from URI. Please ensure it's included, e.g., mongodb://localhost:27017/maadb")
        client.close()
        return

    person_collection = db.person
    print(f"Connected to database: '{db.name}', collection: '{person_collection.name}'")

    updated_count = 0
    processed_count = 0
    errors_count = 0

    print("\nStarting migration of email fields...")
    # Find only documents where 'email' is a string.
    # This helps prevent re-processing if the script is run multiple times.
    cursor = person_collection.find({"email": {"$type": "string"}})

    async for person_doc in cursor:
        processed_count += 1
        original_email_string = person_doc.get("email", "")  # Default to empty string if somehow null

        if not isinstance(original_email_string, str):
            # This case should not be hit due to the query filter, but as a safeguard:
            print(
                f"Skipping doc ID {person_doc['_id']}: email field is not a string ('{type(original_email_string)}').")
            continue

        if not original_email_string.strip():  # Handles empty string or string with only spaces
            new_email_array = []
        else:
            # Split by semicolon, strip whitespace from each resulting email,
            # and filter out any empty strings that might arise (e.g., from "email1;;email2")
            new_email_array = [
                email.strip() for email in original_email_string.split(';') if email.strip()
            ]

        try:
            result = await person_collection.update_one(
                {"_id": person_doc["_id"]},
                {"$set": {"email": new_email_array}}
            )
            if result.modified_count > 0:
                updated_count += 1
                if processed_count <= 20 or processed_count % 100 == 0:  # Log some initial updates and then periodically
                    print(f"  Updated doc ID {person_doc['_id']}: '{original_email_string}' -> {new_email_array}")
            elif result.matched_count > 0 and result.modified_count == 0:
                # This could happen if the transformation results in the same state,
                # e.g., an empty string email was already represented by an empty array somehow,
                # or the new array is identical to an existing one (unlikely if it was a string before).
                if processed_count <= 20 or processed_count % 100 == 0:
                    print(
                        f"  Doc ID {person_doc['_id']} matched but was not modified. Original: '{original_email_string}', New Array: {new_email_array}")
            else:
                # This is highly unlikely as we just fetched the document.
                print(f"  Warning: Doc ID {person_doc['_id']} was not found for update. This is unexpected.")
        except Exception as e:
            errors_count += 1
            print(f"  ERROR updating doc ID {person_doc['_id']}: {e}")
            # Optionally, you might want to store problematic IDs for later review.

    print("\n--- Migration Summary ---")
    print(f"Documents queried (where 'email' was a string): {processed_count}")
    print(f"Documents successfully updated: {updated_count}")
    print(f"Errors during update: {errors_count}")

    if processed_count > 0:  # If any string emails were found and processed
        print("\nRECOMMENDATION:")
        print(
            "After verifying the migration, it's highly recommended to create a multikey index on the 'email' field "
            "for efficient querying.")
        print("You can do this in the MongoDB shell using a command like:")
        print(f"  use {db.name};")
        print(f"  db.{person_collection.name}.createIndex({{ \"email\": 1 }})")
        print(
            "\nThis will allow MongoDB to efficiently query for documents where the 'email' array contains a specific email.")
    elif errors_count == 0:
        print("No documents with string-type email fields found to migrate, or all documents were already processed.")
    else:
        print("Migration finished with errors. Please review the logs.")

    client.close()
    print("\nMongoDB connection closed.")


if __name__ == "__main__":
    # Ensure your config.py is in the same directory or Python's path
    try:
        asyncio.run(migrate_emails_to_array())
    except ImportError:
        print(
            "Error: Could not import 'config'. Ensure 'config.py' is in the current directory or accessible in your PYTHONPATH.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")