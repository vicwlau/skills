# Strong Typing with Pydantic

Define models in a `models/` directory. Use separate schemas for Creating and Updating to handle optional fields correctly.

## Key Rules
- **Explicit Wrappers**: If your API clients wrap payloads in a `data` key, the router must handle the unwrap using a Pydantic model.
- **Serialization**: Use `model_dump(mode='json')` to ensure Pydantic-specific types (like `HttpUrl`, `datetime`, or `Enum`) are converted to primitives Firestore understands.

## Implementation Example (`models/task.py`)

```python
from pydantic import BaseModel
from typing import Optional

class TaskCreate(BaseModel):
    title: str
    priority: int = 1

class TaskUpdate(BaseModel):
    title: Optional[str] = None
    priority: Optional[int] = None

# Wrapper classes automatically handle the validation of nested JSON
class TaskCreatePayload(BaseModel):
    data: TaskCreate

class TaskUpdatePayload(BaseModel):
    data: TaskUpdate
```

## Router Integration

```python
@router.post("/{task_id}")
def create_task(
    task_id: str, 
    payload: TaskCreatePayload, 
    repo: FirestoreRepository = Depends(get_task_repo)
):
    # use model_dump(mode='json') for Firestore compatibility
    return repo.create(task_id, payload.data.model_dump(mode='json'))
```
