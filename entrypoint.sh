#!/bin/bash

# Ensure Python can find the db directory by modifying the PYTHONPATH
export PYTHONPATH=/app:$PYTHONPATH

# Check if INIT_DB is set to true, and if so, run the database initialization script
if [ "$INIT_POSTGRES" = "true" ]; then
  echo "Initializing database..."
  echo "Postgres initialization starting..."
  python db/init_postgres.py
  echo "Postgres initialization finished."
fi
if [ "$INIT_MONGODB" = "true" ]; then
  echo "Initializing database..."
  echo "MongoDB initialization starting..."
  python db/init_mongodb.py
  echo "MongoDB initialization finished..."
fi
if [ "$INIT_NEO4J_NODES" = "true" ]; then
  echo "Initializing database..."
  echo "Neo4j nodes initialization starting..."
  python db/init_neo4j_nodes.py
  echo "Neo4j nodes initialization finished..."
fi
if [ "$INIT_NEO4J_REL" = "true" ]; then
  echo "Initializing database..."
  echo "Neo4j initialization starting..."
  python db/init_neo4j_relationships.py
  echo "Neo4j initialization finished..."
fi
echo -e "\033[1;32m#### Database initialization complete. ####\033[0m"


# Start FastAPI with Uvicorn
echo "Starting FastAPI application..."
uvicorn main:app --host 0.0.0.0 --port 80 --reload &

# Start Streamlit
echo "Starting Streamlit..."
streamlit run frontend/app.py --server.address=0.0.0.0 --server.port=8000