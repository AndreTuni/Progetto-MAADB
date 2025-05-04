#!/bin/bash

# Ensure Python can find the db directory by modifying the PYTHONPATH
export PYTHONPATH=/app:$PYTHONPATH

# Check if INIT_DB is set to true, and if so, run the database initialization script
if [ "$INIT_DB" = "true" ]; then
  echo "Initializing database..."
#  echo "Postgres initialization starting..."
#  python db/init_postgres.py
#  echo "Postgres initialization finished."
#  echo "MongoDB initialization starting..."
#  python db/init_mongodb.py
#  echo "MongoDB initialization finished..."
  echo "Neo4j initialization starting..."
  python db/init_neo4j.py
  echo "Neo4j initialization finished..."
  echo "Database initialization complete."
fi

# Start Streamlit
echo "Starting Streamlit..."
streamlit run frontend/app.py --server.address=0.0.0.0 --server.port=8000