#!/bin/bash

# Check if INIT_DB is set to true, and if so, run the database initialization script
if [ "$INIT_DB" = "true" ]; then
  echo "Initializing database..."
  python db/init_script.py  # Adjust this to your actual Python script path
  echo "Database initialization complete."
fi

# Start Streamlit
echo "Starting Streamlit..."
streamlit run frontend/app.py --server.address=0.0.0.0 --server.port=8000