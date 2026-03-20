# Production Checklist & Deployment

## Debugging and Optimization
- **Global Exception Handler**: Implement in `main.py` to catch `500` errors and log tracebacks.
- **Async Concurrency**: Use `firestore.AsyncClient()` for high-throughput environments to avoid blocking the event loop.
- **Update Logic**: When using `update()`, use `model_dump(exclude_unset=True)` to avoid overwriting existing data with `None`.

## Cloud Run / Functions Gen 2 Deployment

Google Cloud uses **Buildpacks** for source-based deployments.

### Key Deployment Rules:
1. **No Dockerfile Required**: Source-based deployment optimizes the container naturally.
2. **Package Manager**: For `uv`, set the build environment variable:
   ```bash
   gcloud run deploy my-service --source . --set-build-env-vars GOOGLE_PYTHON_PACKAGE_MANAGER=uv
   ```
3. **Environment Isolation**: Ensure `.env` is ignored via `.gitignore` or `.gcloudignore`. Rely on Pydantic `pydantic-settings` to manage production defaults.
4. **Local Auth**: Run `gcloud auth application-default login` for local development against live services.
