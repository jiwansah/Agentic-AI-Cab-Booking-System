
import pytest

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db.database import Base
from app.db import orm_models  # noqa: F401


@pytest.fixture
def db():
    """
    Provide an isolated SQLite database session for each test.

    This avoids modifying your development PostgreSQL database.
    """
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    TestingSessionLocal = sessionmaker(
        bind=engine,
        autoflush=False,
        expire_on_commit=False,
    )

    session = TestingSessionLocal()

    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()
