# Installation Guide

This document will guide you through the process of setting up and running the FastAPI project in both development and production environments.

## Prerequisites

Before you begin, ensure you have the following tools installed on your system:

### 1. UV (Python Package Installer)

UV is a fast Python package installer and resolver written in Rust.

```bash
# Using curl (recommended)
curl -LsSf https://astral.sh/uv/install.sh | sh
```

📚 For more information, visit [UV's official documentation](https://github.com/astral-sh/uv).

### 2. Docker and Docker Compose

Docker is required to run services like PostgreSQL, Redis, and other dependencies.

```bash title="Install Docker on Debian"
# Add Docker's official GPG key:
sudo apt-get update
sudo apt-get install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt-get update
```

To install the latest version, run:

```bash
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
```

🐳 For detailed installation instructions, visit [Docker's official website](https://docs.docker.com/engine/install/).

### 3. Git

Git is required to clone the project repository.

```bash
# Install Git on Ubuntu
sudo apt-get install git

# Install Git on macOS
brew install git

# For Windows, download Git
# https://git-scm.com/download/win
```

🔄 For more information, visit [Git's official website](https://git-scm.com/).

### 4. Psycopg2 Dependencies

To compile psycopg2 (PostgreSQL adapter for Python), you'll need to install the following packages:

For Debian-based distributions (Ubuntu, Debian):
```bash
sudo apt install build-essential libpq-dev python3-dev clang
```

For RPM-based distributions (Fedora, CentOS, RHEL):
```bash
sudo dnf install libpq-dev python3-devel clang
```

🔧 These packages provide the necessary development files to build the psycopg2 extension.

## Development Environment Setup

Follow these steps to set up the project for development:

### 1. Clone the Project

```bash
git clone [project-repository-url]
cd fastapi-boilerplate
```

### 2. Create Virtual Environment and Install Dependencies

```bash
make install
```

This command will create a Python virtual environment and install all necessary dependencies.

### 3. Configure Environment Variables

Create a `.env` file based on the provided example:

```bash
cp .env-example .env
```

!!! warning
    For development environment, you don't need to define the following variables:

    - POSTGRES_USER
    - POSTGRES_PASSWORD
    - POSTGRES_DB
    - PGADMIN_EMAIL
    - PGADMIN_PASSWORD
    - PGADMIN_PORT

### 4. Start Required Services

Start database, Redis, and other required services using Docker Compose:

```bash
make docker-dev-up
```

💡 This will spin up all necessary containers for local development.

### 5. Apply Database Migrations

```bash
make migrate
```

This ensures your database schema is up to date.

### 6. Run the Project

```bash
make start
```

🚀 Your FastAPI application should now be running!

### 7. Access API Documentation

You can view the project's API documentation at:

- Swagger UI: [http://localhost:8000/docs](http://localhost:8000/docs)
- ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)

## Production Environment Setup

For running the project in production mode, follow these steps:

### 1. Configure Environment Variables

In your `.env` file, make sure to define the following variables:

```bash title=".env"
POSTGRES_USER=your_postgres_user
POSTGRES_PASSWORD=your_secure_password
POSTGRES_DB=your_database_name
PGADMIN_EMAIL=your_email@example.com
PGADMIN_PASSWORD=your_pgadmin_password
PGADMIN_PORT=your_pgadmin_port
```

In `config.py` file, make sure to define the following variables:

```python title="config.py"
class Config(BaseConfig):
    """
    Main configuration settings for the FastAPI application.

    This class extends the `BaseConfig` and provides specific configuration values
    for the application, including database URLs, Redis connection, security settings,
    and other operational parameters.
    """

    # previous config

    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgresql"
    POSTGRES_DB: str = "boilerplate"
    PGADMIN_EMAIL: str = "admin@email.com"
    PGADMIN_PASSWORD: str = "pg@pass"
    PGADMIN_PORT: int = 5050


config: Config = Config()
```

??? warning
    🔒 Use strong passwords in production environments!

### 2. Start Production Services

Run Docker Compose in production mode:

```bash
make docker-up
```

⚠️ In production mode:

- Swagger UI and ReDoc will not be accessible
- Your API will be available at [http://localhost:8000](http://localhost:8000)
- Use tools like `Postman` or `cURL` to interact with your API endpoints

## Running Tests

To run the project's test suite:

```bash
make test
```

✅ This command will execute all tests and display the results.

## Debugging with VSCode

For setting up debugging in Visual Studio Code:

### 1. Create Debug Configuration

Create the directory and configuration file:

```bash
mkdir -p .vscode
touch .vscode/launch.json
```

### 2. Configure launch.json

Add the following configuration to `.vscode/launch.json`:

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI",
            "type": "debugpy",
            "request": "launch",
            "program": "${workspaceFolder}/main.py",
            "console": "integratedTerminal",
            "justMyCode": false,
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            },
            "envFile": "${workspaceFolder}/.env"
        }
    ]
}
```

### 3. Start Debugging

1. Open the project in VSCode
2. Go to the "Run and Debug" panel (or press `F5`)
3. Select the "FastAPI" configuration
4. Start debugging

🐞 You can now set breakpoints and debug your FastAPI application within VSCode.

## Troubleshooting

If you encounter any issues during setup:

1. Ensure all prerequisites are correctly installed
2. Verify your `.env` file contains the correct configuration
3. Check Docker logs for any service-specific errors:
   ```bash
   docker compose logs
   ```
4. Make sure the required ports (8000, etc.) are not in use by other applications
