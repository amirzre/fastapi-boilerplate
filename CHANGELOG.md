# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/) and this project adheres to [Semantic Versioning](https://semver.org/).

## [Unreleased]
### Added
- Placeholder for upcoming changes prior to the next release.

## [1.0.0] - 2025-05-10
### Added
- **Authentication & Authorization**  
  - Token-based auth with JWT, role-based access control, and session middleware.  
  - Endpoints: `/auth/login`, `/auth/logout`, `/auth/refresh`.

- **User Management**  
  - CRUD operations for users via `/users` routes.  
  - Password hashing, validation, and user schemas.

- **Posts API**  
  - CRUD operations for posts via `/posts` routes.  
  - Pagination, filtering, and validation schemas.

- **Monitoring & Health Check**  
  - `/health` endpoint for liveness and readiness probes.

- **Core Architecture**  
  - Layered structure with `controllers`, `models`, `repositories`, and `schemas`.  
  - Database mixins for identifiers and timestamps.  
  - Alembic migrations for `users` and `posts` tables.

- **Caching**  
  - Redis backend support with pluggable key makers and cache tagging.

- **Internationalization (i18n)**  
  - Translations setup with Babel and message catalogs.

- **Utilities & Middleware**  
  - Logging, response timing, session management, CORS, and SQLAlchemy middleware.

- **Docker & Deployment**  
  - Development & production Dockerfiles and Compose configurations.  
  - Entrypoint script for container initialization.

- **Documentation**  
  - MkDocs site with pages for installation, configuration, and feature guides.  
  - `docs/` folder includes authentication, authorization, caching, and migrations docs.

- **Testing & CI**  
  - Pytest suite covering API, controllers, repositories, and core modules.  
  - Ruff linting, type checks, and GitHub Actions CI workflow.

### Changed
- Project restructured into `api/v1` vs. `app` separation for routing vs. business logic.
