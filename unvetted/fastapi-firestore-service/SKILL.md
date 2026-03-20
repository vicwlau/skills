---
name: fastapi-firestore-service
description: Architecture for building scalable FastAPI services with Google Cloud Firestore, featuring the Repository Pattern, modular routing, and mock-based local testing.
---

# FastAPI + Firestore Service Architecture

This skill provides a production-ready architecture for building REST APIs using FastAPI and Google Cloud Firestore. It emphasizes modularity, strong typing, and environment-agnostic testing.

## Workflow Overview

1.  **Dependency Management**: Use `uv` to manage production and dev dependencies.
    - `uv add fastapi uvicorn google-cloud-firestore pydantic-settings`
    - `uv add --dev pytest httpx`
2.  **Generic Repository**: Implement a [Repository Pattern](references/REPOSITORY_PATTERN.md) to decouple database logic from routers.
3.  **Data Modeling**: Define [Pydantic models](references/MODELING_GUIDE.md) in a `models/` directory using explicit `data` wrappers for payload validation.
4.  **Modular Routing**: Group resources using `APIRouter` and inject repositories via FastAPI's `Depends`.
5.  **Local Testing**: Use [In-Memory Mocks](references/TESTING_STRATEGIES.md) for fast unit testing and separate E2E tests for infrastructure verification.
6.  **Deployment**: Deploy via Google Cloud [Buildpacks](references/DEPLOYMENT_CHECKLIST.md) using source-based deployment.

## Core Best Practices

- **Separation of Concerns**: Keep database logic in repositories, validation in models, and business logic in routers.
- **Dependency Injection**: Always inject database managers or repositories into routes to facilitate mocking.
- **Production Safety**: Use `AsyncClient` for high-concurrency and `exclude_unset=True` during updates.

## Deep Dive References

- [Repository Pattern & Database Layer](references/REPOSITORY_PATTERN.md)
- [Strong Typing & Data Modeling](references/MODELING_GUIDE.md)
- [Mocking & Testing Strategy](references/TESTING_STRATEGIES.md)
- [Production & Deployment Checklist](references/DEPLOYMENT_CHECKLIST.md)
