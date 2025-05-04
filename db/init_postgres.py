import os
import pandas as pd
import psycopg2
from dotenv import load_dotenv
from io import StringIO

load_dotenv()

DB_PARAMS = {
    "dbname": os.getenv("POSTGRES_DB", "maadb"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", "password"),
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432")
}

TABLES = {
    "place": {
        "columns": {
            "id": "INTEGER PRIMARY KEY",
            "name": "TEXT",
            "url": "TEXT",
            "type": "TEXT",
            "PartOfPlaceId": "INTEGER"
        },
        "csv": ["/app/data/static/Place/part-00000-5d3b389c-4734-4de7-a476-66a0fe967afc-c000.csv"],
        "fk": ['ALTER TABLE place ADD FOREIGN KEY ("PartOfPlaceId") REFERENCES place(id);']
    },
    "organization": {
        "columns": {
            "id": "INTEGER PRIMARY KEY",
            "type": "TEXT",
            "name": "TEXT",
            "url": "TEXT",
            "LocationPlaceId": "INTEGER"
        },
        "csv": ["/app/data/static/Organisation/part-00000-1b7378fc-ddc5-45ae-a217-23037b649081-c000.csv"],
        "fk": ['ALTER TABLE organization ADD FOREIGN KEY ("LocationPlaceId") REFERENCES place(id);']
    },
    "tagclass": {
        "columns": {
            "id": "INTEGER PRIMARY KEY",
            "name": "TEXT",
            "url": "TEXT",
            "SubclassOfTagClassId": "INTEGER"
        },
        "csv": ["/app/data/static/TagClass/part-00000-4dea37c1-863e-4d43-adfe-95d3ae0a86a9-c000.csv"],
        "fk": ['ALTER TABLE tagclass ADD FOREIGN KEY ("SubclassOfTagClassId") REFERENCES tagclass(id);']
    },
    "tag": {
        "columns": {
            "id": "INTEGER PRIMARY KEY",
            "name": "TEXT",
            "url": "TEXT",
            "TypeTagClassId": "INTEGER"
        },
        "csv": ["/app/data/static/Tag/part-00000-4bdec47c-71f2-4e9a-9b75-2a8f7b011870-c000.csv"],
        "fk": ['ALTER TABLE tag ADD FOREIGN KEY ("TypeTagClassId") REFERENCES tagclass(id);']
    }
}


def connect():
    return psycopg2.connect(**DB_PARAMS)


def create_tables(cursor):
    for table, config in TABLES.items():
        cursor.execute(f"DROP TABLE IF EXISTS {table} CASCADE;")
        columns = ", ".join(f'"{col}" {type_}' for col, type_ in config["columns"].items())
        cursor.execute(f"CREATE TABLE {table} ({columns});")


def load_csvs(cursor, table, config):
    int_columns = [col for col, type_ in config["columns"].items() if type_.startswith("INTEGER")]

    for path in config["csv"]:
        print(f"Loading {path} into {table}")
        for chunk in pd.read_csv(path, sep="|", chunksize=1000):
            if chunk.empty:
                continue

            chunk.drop_duplicates(subset=["id"], inplace=True)

            # Convert float-looking integers (like 64.0) to actual integers
            for col in int_columns:
                if col in chunk.columns:
                    chunk[col] = pd.to_numeric(chunk[col], errors='coerce')
                    chunk[col] = chunk[col].dropna().astype('Int64')  # Nullable integers

            buffer = StringIO()
            chunk.to_csv(buffer, sep="|", header=False, index=False, na_rep="NULL")
            buffer.seek(0)

            cursor.copy_expert(f"""
                COPY {table} ({', '.join(f'"{col}"' for col in chunk.columns)})
                FROM STDIN WITH (FORMAT CSV, DELIMITER '|', NULL 'NULL');
            """, buffer)


def add_foreign_keys(cursor):
    for config in TABLES.values():
        for constraint in config["fk"]:
            cursor.execute(constraint)


def main():
    print("Starting PostgreSQL import...")
    with connect() as conn:
        cursor = conn.cursor()
        create_tables(cursor)
        conn.commit()

        for table, config in TABLES.items():
            load_csvs(cursor, table, config)
        conn.commit()

        add_foreign_keys(cursor)
        conn.commit()
    print("PostgreSQL import complete.")


if __name__ == "__main__":
    main()
