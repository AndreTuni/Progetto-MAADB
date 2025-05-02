from fastapi import FastAPI
from db.mongo_client import db
from db.neo4j_client import driver, get_friends_of
from db.postgres import conn

app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}

@app.get("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}


# ➕ MongoDB sample data
@app.post("/mongo/init")
async def init_mongo():
    person = {"name": "Alice", "email": "alice@example.com"}
    await db.people.insert_one(person)
    return {"message": "Inserted into MongoDB"}

# ➕ Neo4j sample data
@app.post("/neo4j/init")
async def init_neo4j():
    with driver.session() as session:
        session.run("CREATE (:Person {name: 'Alice'})")
        session.run("CREATE (:Person {name: 'Bob'})")
        session.run("""
            MATCH (a:Person {name: 'Alice'}), (b:Person {name: 'Bob'})
            CREATE (a)-[:KNOWS]->(b)
        """)
    return {"message": "Inserted into Neo4j"}

# 🔍 Basic MongoDB query
@app.get("/mongo/person/{name}")
async def get_person(name: str):
    person = await db.people.find_one({"name": name})
    if person:
        return {"email": person["email"]}
    return {"error": "Not found"}

# 🔍 Basic Neo4j query
@app.get("/neo4j/friends/{name}")
async def get_friends(name: str):
    friends = get_friends_of(name)
    return {"friends": friends}

# 🔀 Cross-database query
@app.get("/cross/{name}")
async def cross_query(name: str):
    person = await db.people.find_one({"name": name})
    friends = get_friends_of(name)
    return {
        "person": {
            "name": name,
            "email": person["email"] if person else None
        },
        "friends": friends
    }


@app.post("/postgres/init")
def init_postgres():
    with conn.cursor() as cur:
        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id SERIAL PRIMARY KEY,
                name TEXT,
                email TEXT
            );
        """)
        cur.execute("""
            INSERT INTO users (name, email)
            VALUES ('Alice', 'alice@example.com')
            ON CONFLICT DO NOTHING;
        """)
        conn.commit()
    return {"message": "Initialized PostgreSQL"}

@app.get("/postgres/user/{name}")
def get_pg_user(name: str):
    with conn.cursor() as cur:
        cur.execute("SELECT name, email FROM users WHERE name = %s", (name,))
        row = cur.fetchone()
        if row:
            return {"name": row[0], "email": row[1]}
        else:
            return {"error": "User not found"}
