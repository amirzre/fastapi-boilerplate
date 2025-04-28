#!/bin/sh
set -e

echo "Running database migrations..."
uv python3 init.py

echo "Starting application..."
exec uv python3 main.py
