---
name: SQLAlchemy 2.0 3-Tier Architecture
description: Instructions for the LLM on how to generate a thin SQLAlchemy wrapper with a clean separation of Data Schema, Engine, and CRUD tools.
---

# CONTEXT AND GOAL
When asked to write or structure database code using SQLAlchemy 2.0, you must adhere to a strict 3-tier architecture. 
The goal is to maintain a thin, flexible wrapper around collections of data where the USER focuses on designing the **Data Schema**, and you focus on writing the **CRUD Tools** and the **Engine**, keeping them completely decoupled.

# CORE ARCHITECTURE PRINCIPLES

Always separate the code into these 3 distinct sections (either separated by clear comment headers or in separate files):

## 1. DATA SCHEMA (MODELS)
This is where the USER will spend most of their time customizing the structure.
- **Base Class**: Use SQLAlchemy 2.0 `DeclarativeBase`.
- **Infrastructure boilerplate**:
  - Implement a standard `MetaData` naming convention (`ix`, `uq`, `ck`, `fk`, `pk`).
  - Override `__tablename__` in the `Base(DeclarativeBase)` class using `@declared_attr.directive` to automatically convert `PascalCase` class names to `snake_case` table names.
- **Typing**: Use `Mapped[type]` and `mapped_column()` for all fields.
- **Type Aliases**: Emulate `Annotated` type aliases for repetitive columns to keep the schema highly readable and clean. E.g.:
  - `PK`: `Annotated[str | int, mapped_column(primary_key=True)]`.
  - `Timestamp`: `Annotated[datetime, mapped_column(server_default=func.now())]`.
  - `UpdatedAt`: `Annotated[datetime, mapped_column(server_default=func.now(), onupdate=func.now())]`.
  - `Str` / `OptStr`: Shortcuts for strings and optional strings.
- **Timestamp Strategy**: Always use `server_default=func.now()` for creation times and `onupdate=func.now()` for update tracking. This delegates timestamp generation directly to the database engine. It guarantees perfect consistency across different application instances and prevents insidious application-level timezone drift bugs.
- **Column Formatting**: In the Model classes, use spaces to vertically align the types (e.g., `Mapped[...]`) so they start at the exact same horizontal position. This creates a highly readable, table-like layout for the entire schema.
- **Relationships & Refactor Safety**: 
  - Define `relationship()` explicitly with `back_populates`.
  - Always use a helper function `ref(prop: Any) -> str` to extract attribute keys for `back_populates` (e.g., `back_populates=ref(User.posts)`).
  - Use `cascade="all, delete-orphan"` for parent-to-child relations.
- **Constraints**: Use `UniqueConstraint` defined in `__table_args__` for multi-column uniqueness.

## 2. ENGINE (DATABASE MANAGER)
This section must be **completely domain-agnostic**. It should not know anything about the specific models (e.g., Users, Emails, Sermons).
- Its only responsibility is to manage the `create_engine`, connection pooling, and provide a `Session` factory or context manager.
- Implement a `@contextmanager` named `session_scope()` to handle automatic transaction commits, rollbacks, and session closing gracefully.
- For SQLite specifically, provide intuitive arguments (like `file_name` and an optional `dir_path`) instead of a bare `db_url` so it's easy for the USER to choose where a local database file is saved. Handle absolute and relative paths seamlessly using Python's `os` module.
- This layer allows cleanly managing databases by utilizing standard Python abstractions.
- Support raw SQL "escape hatches" via `execute_query(sql, params)`.
- **CRITICAL:** Do NOT include domain-specific query logic (like `add_emails` or `get_sermons`) in this class. 

## 3. FUNCTIONS / TOOLS (QUERIES)
This is where you (the LLM) will generate common CRUD-like functions based on the data schema.
- **Format**: Write these as standalone functions, or bundle them into domain-specific "Service" or "Repository" objects (e.g., `EmailQueries(db_manager)`). 
- **Dependency Injection**: Query functions should accept either a `Session` object or the `DatabaseManager` as an argument (or be initialized with one). This explicitly decouples the queries from the database connection logic.
- **Common Features**:
  - Implement `ilike` filters for search methods.
  - Implement methods to return `Set[str]` or IDs for fast local sync/state checks.
  - Implement a visual preview like a `print_table` or formatted summary output for tool-calling/debugging.
- **SQLAlchemy 2.0 Syntax**: Strictly use `select()`, `update()`, `delete()`, and execute them via `session.scalars(stmt).all()`.

# TEMPLATE EXAMPLE

```python
from typing import Annotated, List, Optional, Any
from datetime import datetime, timezone
from contextlib import contextmanager
from sqlalchemy import create_engine, String, DateTime, select, MetaData, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, Session, declared_attr, relationship

# ==========================================
# 1. DATA SCHEMA
# ==========================================

NAMING_CONVENTION = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

def ref(prop: Any) -> str:
    """Extracts attribute name for back_populates for refactor-safety."""
    return prop.key if hasattr(prop, "key") else prop.__name__

class Base(DeclarativeBase):
    metadata = MetaData(naming_convention=NAMING_CONVENTION)

    @declared_attr.directive
    def __tablename__(cls) -> str:
        return "".join(["_" + i.lower() if i.isupper() else i for i in cls.__name__]).lstrip("_")


# Reusable Type Aliases make the schema incredibly readable
PK = Annotated[int, mapped_column(primary_key=True)]
Str30 = Annotated[str, mapped_column(String(30))]
OptStr = Annotated[Optional[str], mapped_column(String)]
Timestamp = Annotated[datetime, mapped_column(DateTime, server_default=func.now())]
UpdatedAt = Annotated[datetime, mapped_column(DateTime, server_default=func.now(), onupdate=func.now())]

class User(Base):
    id:         Mapped[PK]
    username:   Mapped[Str30]
    bio:        Mapped[OptStr]
    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]
    
    # Relationships
    posts:      Mapped[List["Post"]] = relationship(back_populates="user", cascade="all, delete-orphan")

class Post(Base):
    id:         Mapped[PK]
    content:    Mapped[Str30]
    user_id:    Mapped[int] = mapped_column(index=True) # Define foreign key setup...
    
    # Refactor safe relationship
    user:       Mapped[User] = relationship(back_populates=ref(User.posts))

# ==========================================
# 2. ENGINE (DB MANAGER)
# ==========================================
class DatabaseManager:
    """Domain-agnostic database manager for connection handling."""
    def __init__(self, file_name: str = "app.db", dir_path: Optional[str] = None):
        import os
        if dir_path:
            os.makedirs(dir_path, exist_ok=True)
            db_path = os.path.join(dir_path, file_name)
        else:
            db_path = file_name
            
        db_url = f"sqlite:///{db_path}"
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
    
    def get_session(self) -> Session:
        return Session(self.engine)

    @contextmanager
    def session_scope(self):
        """Provide a transactional scope around a series of operations."""
        session = Session(self.engine)
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()

    def execute_query(self, query: str, params: dict[str, Any] | None = None):
        with self.engine.connect() as conn:
            from sqlalchemy import text
            result = conn.execute(text(query), params or {})
            return result.fetchall()


# ==========================================
# 3. FUNCTIONS / TOOLS (QUERIES)
# ==========================================
# Standalone functions that take a `Session` directly (Dependency Injection)
# This perfectly separates query logic from engine connection logic.

def create_user(session: Session, username: str) -> User:
    user = User(username=username)
    session.add(user)
    session.commit()
    return user

def get_recent_users(session: Session, limit: int = 5) -> List[User]:
    stmt = select(User).order_by(User.created_at.desc()).limit(limit)
    return list(session.scalars(stmt).all())
```
