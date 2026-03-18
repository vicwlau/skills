# Testing & Mocking Strategies

Testing against a live Firestore instance locally can be slow or prone to gRPC timeout hangs. Modular architecture allows for seamless mocking.

## 1. The In-Memory Mock (Dependency Override)

Create a fake repository that stores data in a simple Python dictionary. Use FastAPI's `dependency_overrides` to swap this in during tests.

```python
class MockRepository:
    def __init__(self, collection_name: str):
        self.storage = {}
    
    def create(self, doc_id: str, data: dict):
        self.storage[doc_id] = data
        return data

    def get(self, doc_id: str):
        return self.storage.get(doc_id)
    
    # ... implement others ...
```

## 2. Test Organization

Tests should be strictly separated by speed and network usage.

```text
tests/
├── unit/                # Fast, isolated tests (No network, no real DB)
│   ├── test_models.py   # Test Pydantic validation cleanly
│   └── test_api.py      # Test routers purely using the In-Memory Mock
└── e2e/                 # Slower, live infrastructure tests
    └── verify_api.py    # e.g., using `requests` to hit the Live Cloud Run URL
```

## 3. Applying Overrides in Pytest

```python
from main import app
from routers.tasks import get_task_repo

def test_create_task():
    # Swap real repo for mock
    app.dependency_overrides[get_task_repo] = lambda: MockRepository("tasks")
    # ... run tests using TestClient ...
    app.dependency_overrides.clear()
```
