# FastAPI Boilerplate

Welcome to **FastAPI Boilerplate**, a production-ready starter kit that helps you spin up a modern, fully-asynchronous REST API in minutes. Built on FastAPI and Pydantic V2, it combines the best of Python’s type-safe world with battle-tested data persistence (SQLAlchemy V2 + PostgreSQL) and blazing-fast caching (Redis). Everything is containerized via Docker Compose so you can go from zero to API in one command.

---

## 🚀 Features

- **⚡️ Fully asynchronous**  
  All endpoints, database calls, and background tasks use `async`/`await` for maximum concurrency.
- **🔐 JWT-based authentication**  
  Secure access and refresh tokens, stored in cookies, with customizable scopes and roles.
- **🍪 Cookie-based token management**  
  HTTP-only cookies for access & refresh tokens to mitigate XSS/CSRF.
- **🏬 Redis caching**  
  Easy, pluggable caching layer with tag-based invalidation.
- **⚙️ Robust SQLAlchemy queries**  
  Use SQLAlchemy V2’s new asyncio API, optimized with select / join strategies.
- **⎘ Pagination support**  
  Offset and cursor-based pagination out of the box.
- **🦾 Extendable modules**  
  Clean separation of controllers, repositories, schemas, and core utilities.
- **🤸‍♂️ Flexible architecture**  
  Mixins for shared models, customizable middlewares, and dependency overrides.
- **🚚 Docker Compose**  
  One-command setup for Dev & Prod, with health checks, migrations, and env-based configs.

---

## 🛠 Technologies

- **FastAPI**: Modern, fast (high-performance), web framework for building APIs with Python 3.12+  
- **Pydantic V2**: Data parsing & validation library, now rewritten in Rust for speed  
- **SQLAlchemy V2**: Python SQL toolkit & ORM with full asyncio support  
- **PostgreSQL**: Advanced open-source relational database  
- **Redis**: In-memory data store for caching, pub/sub, rate-limiting  
- **Docker & Docker Compose**: Containerization and multi-service orchestration
- **uv**: An extremely fast Python package and project manager

---

## 🏗️ Project Structure

```text
fastapi-boilerplate
├── alembic.ini
├── api/
│   └── v1/
│       ├── auth/          # API routes for authentication
│       ├── monitoring/    # Health checks & metrics
│       ├── posts/         # Post CRUD endpoints
│       └── users/         # User CRUD endpoints
├── app/
│   ├── controllers/       # Business logic & input validation
│   ├── models/            # SQLAlchemy models & mixins
│   ├── repositories/      # DB access & query methods
│   └── schemas/           # Pydantic request/response schemas
├── core/
│   ├── cache/             # Cache backends & key makers
│   ├── db/                # Session, transactions, mixins
│   ├── exceptions/        # Custom exception classes
│   ├── fastapi/           # Dependencies, middlewares, ACL
│   ├── security/          # JWT, password hashing, ACL
│   └── utils/             # Validators, i18n, logging
├── docker/                # Dockerfiles (dev & prod)
├── docker-compose.yml     # Compose config for all services
├── main.py                # FastAPI app entrypoint
├── migrations/            # Alembic versioned migrations
├── tests/                 # Pytest suites (unit & integration)
├── translations/          # i18n message catalogs
├── pyproject.toml         # Poetry / project metadata
└── README.md              # This boilerplate’s own documentation
```