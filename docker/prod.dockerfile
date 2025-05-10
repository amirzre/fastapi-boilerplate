FROM python:3.13-slim

# Install system dependencies for psycopg2 (and clang if needed)
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
    build-essential python3-dev libpq-dev clang \
    curl python3-uvicorn \
    && rm -rf /var/lib/apt/lists/*

# Install uv directly into /usr/local/bin
RUN curl -LsSf https://astral.sh/uv/install.sh \
    | env UV_INSTALL_DIR="/usr/local/bin" sh

# Create a non-root user
RUN useradd --create-home --shell /bin/bash appuser
WORKDIR /home/appuser
USER appuser

# Copy project files
COPY --chown=appuser:appuser . .

# Install Python dependencies with uv
RUN uv sync --no-dev

# Expose and launch
EXPOSE 8000
ENTRYPOINT ["uv", "run", "sh", "scripts/entrypoint.sh"]
