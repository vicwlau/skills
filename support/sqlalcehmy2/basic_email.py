from sqlalchemy import create_engine, String, Text, Boolean, DateTime, ForeignKey, select, update
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, sessionmaker, Session, relationship
from datetime import datetime, timezone
from typing import Set, List

class Base(DeclarativeBase):
    pass

class EmailRecord(Base):
    """
    Stores the raw email data as received from the server.
    """
    __tablename__ = "emails"

    id: Mapped[int] = mapped_column(primary_key=True)
    message_id: Mapped[str] = mapped_column(String, unique=True, index=True)
    uid: Mapped[str] = mapped_column(String)
    
    sender: Mapped[str] = mapped_column(String)
    to: Mapped[str] = mapped_column(String)
    subject: Mapped[str] = mapped_column(String)
    body_text: Mapped[str] = mapped_column(Text, nullable=True)
    body_html: Mapped[str] = mapped_column(Text, nullable=True)
    
    received_at: Mapped[datetime] = mapped_column(DateTime)
    is_deleted_on_server: Mapped[bool] = mapped_column(Boolean, default=False)
    synced_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Relationship to insights (One-to-Many, as one email could have multiple agent analyses)
    insights: Mapped[List["EmailInsight"]] = relationship(back_populates="email", cascade="all, delete-orphan")

class EmailInsight(Base):
    """
    Stores AI-generated insights and analysis for a specific email.
    """
    __tablename__ = "email_insights"

    id: Mapped[int] = mapped_column(primary_key=True)
    email_id: Mapped[int] = mapped_column(ForeignKey("emails.id"))
    
    # Metadata for the analysis
    agent_name: Mapped[str] = mapped_column(String) # e.g., "ResearchScout-GPT4"
    model_version: Mapped[str] = mapped_column(String, nullable=True)
    
    # AI Output
    summary: Mapped[str] = mapped_column(Text, nullable=True)
    key_takeaways: Mapped[str] = mapped_column(Text, nullable=True) # JSON or markdown string
    action_items: Mapped[str] = mapped_column(Text, nullable=True)
    
    # Content Categorization
    tag: Mapped[str] = mapped_column(String, nullable=True) # e.g., "research paper", "new tool", "article", etc.
    
    analyzed_at: Mapped[datetime] = mapped_column(DateTime, default=lambda: datetime.now(timezone.utc))

    # Link back to the parent email
    email: Mapped[EmailRecord] = relationship(back_populates="insights")

class DBManager:
    """
    Handles connection and operations for the SQLite database.
    """
    def __init__(self, db_url: str = "sqlite:///emails.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)

    def get_session(self) -> Session:
        return self.Session()

    def get_all_existing_message_ids(self) -> Set[str]:
        """Returns a set of all message_ids already in the local DB."""
        with self.get_session() as session:
            stmt = select(EmailRecord.message_id)
            result = session.execute(stmt)
            return {row[0] for row in result.all()}

    def mark_as_deleted(self, message_ids: List[str]) -> None:
        """Marks emails in the local DB as no longer on the server."""
        if not message_ids:
            return
        with self.get_session() as session:
            stmt = (
                update(EmailRecord)
                .where(EmailRecord.message_id.in_(message_ids))
                .values(is_deleted_on_server=True)
            )
            session.execute(stmt)
            session.commit()

    def add_emails(self, records: List[EmailRecord]) -> None:
        """Bulk adds new email records."""
        if not records:
            return
        with self.get_session() as session:
            session.add_all(records)
            session.commit()

    def preview_emails(self, limit: int = 5, snippet_len: int = 100) -> None:
        """
        Prints a quick, readable summary of the most recent emails in the DB.
        """
        with self.get_session() as session:
            stmt = select(EmailRecord).order_by(EmailRecord.received_at.desc()).limit(limit)
            emails = session.execute(stmt).scalars().all()

            if not emails:
                print("No emails found in the database.")
                return

            print(f"--- Showing last {len(emails)} emails ---")
            for e in emails:
                status = " [GHOST]" if e.is_deleted_on_server else ""
                print(f"ID: {e.id}{status} | {e.sender}")
                print(f"Sub: {e.subject[:60]}...")
                
                # Smart snippet logic
                content = e.body_text if e.body_text and len(e.body_text) > 10 else "[HTML only]"
                snippet = content[:snippet_len].replace('\n', ' ').strip()
                print(f"Snippet: {snippet}...")
                print("-" * 30, "\n")

    def add_insight(self, insight: EmailInsight) -> None:
        """Saves a new AI-generated insight."""
        with self.get_session() as session:
            session.add(insight)
            session.commit()
