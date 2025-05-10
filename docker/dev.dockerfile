# Use a slim Python image for a smaller footprint
FROM python:3.13-slim

# Set environment variables for Python behavior and app home
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    APP_HOME=/app \
    PATH="/root/.local/bin:$PATH"

WORKDIR $APP_HOME

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    python3-dev \
    clang \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Download the latest installer
ADD https://astral.sh/uv/install.sh /uv-installer.sh

# Run the installer then remove it
RUN sh /uv-installer.sh && rm /uv-installer.sh


# Copy pyproject.toml and other dependency files
COPY pyproject.toml uv.lock ./

# Install dependencies with uv
RUN uv sync --locked

# Copy the rest of the application code
COPY . .

# Make entrypoint script executable
RUN chmod +x /app/scripts/entrypoint.sh

# Expose the port the app will run on
EXPOSE 8000

# Run entrypoint script
ENTRYPOINT ["/app/scripts/entrypoint.sh"]
