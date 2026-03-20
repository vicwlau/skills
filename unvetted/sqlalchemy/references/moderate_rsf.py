# type: ignore
# pyright: skip-check
# pytright: reportGeneralTypeIssues=false

from __future__ import annotations
from datetime import datetime
from typing import Annotated, List, Optional, Any
import enum

from sqlalchemy import (
    String,
    Boolean,
    DateTime,
    JSON,
    ForeignKey,
    func,
    UniqueConstraint,
    MetaData,
)
from sqlalchemy.orm import (
    DeclarativeBase,
    Mapped,
    mapped_column,
    relationship,
    declared_attr,
)

# ------------------------------------------------
# SCHEMA
# ------------------------------------------------

# --- 1. Infrastructure ---
ORPHAN_CASCADE = "all, delete-orphan"
DB_CASCADE = "CASCADE"

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
        return "".join(
            ["_" + i.lower() if i.isupper() else i for i in cls.__name__]
        ).lstrip("_")


# --- 2. Type Aliases ---
PK = Annotated[str, mapped_column(primary_key=True)]
Str = Annotated[str, mapped_column(String)]
OptStr = Annotated[Optional[str], mapped_column(String)]
BoolF = Annotated[bool, mapped_column(Boolean, default=False)]
Timestamp = Annotated[datetime, mapped_column(DateTime, server_default=func.now())]
UpdatedAt = Annotated[
    datetime, mapped_column(DateTime, server_default=func.now(), onupdate=func.now())
]


# --- 2. Base & Enums ---
class SeriesType(enum.Enum):
    STANDARD, PODCAST, STANDALONE, LECTURES, AVP, BREAD, OTHER, NOT_CLASSIFIED = range(
        8
    )


class ProgressStatus(enum.Enum):
    NOT_STARTED = "NOT_STARTED"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


# --- 3. Models (Ordered for Dependency Resolution) ---
class Series(Base):
    id: Mapped[PK]
    name: Mapped[str] = mapped_column(unique=True, index=True)
    page_url: Mapped[Str]
    artwork_card_url: Mapped[OptStr]
    type: Mapped[SeriesType] = mapped_column(default=SeriesType.NOT_CLASSIFIED)
    is_skip_processing: Mapped[BoolF]
    skip_processing_reason: Mapped[OptStr]
    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]

    # We use a string for the target class because Sermon is below,
    # but the back_populates will be checked at runtime.
    sermons: Mapped[List[Sermon]] = relationship(back_populates="series")


class Sermon(Base):
    # __tablename__ = "sermon" # not needed bc of __tablename__ in Base with declared_attr
    id: Mapped[PK]
    title: Mapped[str] = mapped_column(unique=True)
    description: Mapped[OptStr]
    raw_date: Mapped[OptStr]
    raw_speaker_name: Mapped[OptStr]
    date: Mapped[Optional[datetime]] = mapped_column(index=True)
    page_url: Mapped[Str]
    audio_url: Mapped[OptStr]
    gs_audio_url: Mapped[OptStr]
    gs_transcript_url: Mapped[OptStr]
    gs_converted_text_url: Mapped[OptStr]
    gs_summary_url: Mapped[OptStr]

    download_status: Mapped[ProgressStatus] = mapped_column(
        default=ProgressStatus.NOT_STARTED
    )
    transcription_status: Mapped[ProgressStatus] = mapped_column(
        default=ProgressStatus.NOT_STARTED
    )
    converted_status: Mapped[ProgressStatus] = mapped_column(
        default=ProgressStatus.NOT_STARTED
    )
    summarized_status: Mapped[ProgressStatus] = mapped_column(
        default=ProgressStatus.NOT_STARTED
    )
    vector_index_status: Mapped[ProgressStatus] = mapped_column(
        default=ProgressStatus.NOT_STARTED
    )

    series_id: Mapped[Optional[str]] = mapped_column(ForeignKey(Series.id), index=True)
    is_essential: Mapped[BoolF]
    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]

    # --- Relationships ---
    series: Mapped[Optional[Series]] = relationship(back_populates=ref(Series.sermons))
    # string backpopulate bc Sermon isn't defined yet
    sermon_speakers: Mapped[List[SermonSpeaker]] = relationship(
        back_populates="sermon", cascade=ORPHAN_CASCADE
    )
    vectors_v1: Mapped[List[SermonVectorV1]] = relationship(
        back_populates="sermon", cascade=ORPHAN_CASCADE
    )


class SermonVectorV1(Base):
    id: Mapped[PK]
    text: Mapped[Str]
    embedding: Mapped[dict] = mapped_column(JSON)  # type: ignore
    dimensions: Mapped[int]
    chunks_index: Mapped[int]
    chunks_total: Mapped[int]
    embedding_model: Mapped[Str]
    sermon_id: Mapped[str] = mapped_column(
        ForeignKey(Sermon.id, ondelete=DB_CASCADE), index=True
    )
    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]

    # --- Relationships ---
    sermon: Mapped[Sermon] = relationship(back_populates=ref(Sermon.vectors_v1))


# Defined outside of class to enable reference of attribute
SermonVectorV1.__table_args__ = (
    UniqueConstraint(SermonVectorV1.sermon_id, SermonVectorV1.chunks_index),
)


class Speaker(Base):
    id: Mapped[PK]
    name: Mapped[str] = mapped_column(unique=True)
    biography: Mapped[OptStr]
    role: Mapped[List[str]] = mapped_column(JSON)
    created_at: Mapped[Timestamp]
    updated_at: Mapped[UpdatedAt]

    # --- Relationships ---
    sermon_speakers: Mapped[List[SermonSpeaker]] = relationship(
        back_populates="speaker", cascade=ORPHAN_CASCADE
    )


class SermonSpeaker(Base):
    sermon_id: Mapped[str] = mapped_column(
        ForeignKey(Sermon.id, ondelete=DB_CASCADE), primary_key=True
    )
    speaker_id: Mapped[str] = mapped_column(
        ForeignKey(Speaker.id, ondelete=DB_CASCADE), primary_key=True
    )

    # --- Relationships ---
    # Refactor-safe: Pulled from classes defined above
    sermon: Mapped[Sermon] = relationship(back_populates=ref(Sermon.sermon_speakers))
    speaker: Mapped[Speaker] = relationship(back_populates=ref(Speaker.sermon_speakers))


# ------------------------------------------------
# DATABASE MANAGER
# ------------------------------------------------


class DatabaseManager:
    def __init__(self, connection_name: str, user: str, password: str, db: str):
        self.connector = Connector()
        self.connection_name = connection_name
        self.user = user
        self.password = password
        self.db = db
        self.pool = self._create_pool()

    def _get_conn(self):
        return self.connector.connect(
            self.connection_name,
            "pg8000",
            user=self.user,
            password=self.password,
            db=self.db,
            ip_type=IPTypes.PUBLIC,
        )

    def _create_pool(self):
        return sqlalchemy.create_engine(
            "postgresql+pg8000://",
            creator=self._get_conn,
        )

    def execute_query(self, query: str, params: dict[str, Any] | None = None):
        with self.pool.connect() as conn:
            result = conn.execute(text(query), params or {})
            return result.fetchall()

    def close(self):
        self.connector.close()


# Usage
def get_db() -> DatabaseManager:
    return DatabaseManager(INSTANCE_CONNECTION, DB_USER, DB_PASS, DB_NAME)


# ------------------------------------------------
# QUERIES
# ------------------------------------------------


def get_sermon_names(match: str):
    """
    Get sermon names that match a given string.
    Args:
        match (str): The string to match sermon titles against.
    Returns:
        str: A formatted string containing the number of sermons found and their titles.
    """

    print(f"executing get sermon names for match: '{match}'...")

    db = get_db()
    with Session(db.pool) as session:
        stmt = select(
            Sermon.title.label("Sermon Title"),
        ).where(Sermon.title.ilike(f"%{match}%"))

    results = session.execute(stmt).all()

    print(f"\n ----- TOOL CALL ----- \n")
    print_table(results, 100)
    print(f"\n ----- TOOL CALL ----- \n")

    return (
        f"Found {len(results)} sermons matching '{match}'. \n"
        + "Here are the titles:\n"
        + "\n".join([f"- {row[0]}" for row in results])
    )
