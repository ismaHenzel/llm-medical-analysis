#!/bin/sh
echo "Running entrypoint"

echo "Applying alembic migrations"
alembic upgrade head

echo "Starting Fastapi Webserver"
fastapi run src/main.py --port 8080 --reload
