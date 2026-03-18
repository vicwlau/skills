# Repository Pattern for Firestore

To avoid duplicating Firestore logic for every new collection, use a **Generic Repository**. This centralizes the interaction with the Google Cloud Client and facilitates dependency injection.

## Implementation Details

### Database Layer (`database.py`)

```python
from google.cloud import firestore
from config import config # Defined using pydantic-settings inside config.py

class FirestoreRepository:
    def __init__(self, collection_name: str):
        # Pass project explicitly so local connections don't hang, dynamically pulled from .env or GCP
        # Note: Consider using firestore.AsyncClient() for non-blocking I/O in production
        self.db = firestore.Client(project=config.PROJECT_ID)
        self.collection = self.db.collection(collection_name)

    def create(self, doc_id: str, data: dict) -> dict:
        doc_ref = self.collection.document(doc_id)
        doc_ref.set(data)
        return doc_ref.get().to_dict()

    def get(self, doc_id: str): 
        doc_ref = self.collection.document(doc_id)
        doc = doc_ref.get()
        return doc.to_dict() if doc.exists else None

    def update(self, doc_id: str, data: dict): 
        doc_ref = self.collection.document(doc_id)
        doc_ref.update(data)
        return doc_ref.get().to_dict()

    def delete(self, doc_id: str): 
        self.collection.document(doc_id).delete()

    def list(self, limit: int = 10, start_after: str = None): 
        # Production ready apps must use cursor-based pagination (start_after)
        query = self.collection.limit(limit)
        if start_after:
            query = query.start_after({u'doc_id': start_after})
        return [doc.to_dict() for doc in query.stream()]
```

## Factory for Dependency Injection

```python
def get_repo(collection_name: str):
    def _get_repo() -> FirestoreRepository:
        return FirestoreRepository(collection_name)
    return _get_repo
```
