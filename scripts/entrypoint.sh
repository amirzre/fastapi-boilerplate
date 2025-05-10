#!/bin/sh
set -e

echo "Running database migrations..."
uv run python init.py

echo "Starting application..."
exec uv run python main.py
