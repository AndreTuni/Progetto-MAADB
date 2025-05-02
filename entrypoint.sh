#!/bin/bash
set -e

# If INIT_DB environment variable is set to true, initialize the databases
if [ "$INIT_DB" = "true" ]; then
    echo "Initializing databases..."
    python db/init_script.py
fi

# Start the application
exec "$@"