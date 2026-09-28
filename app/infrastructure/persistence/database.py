import os

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from app.settings import settings

DATABASE_URL = settings.DATABASE_URL

if DATABASE_URL.startswith("sqlite:///") and not DATABASE_URL.startswith(
    "sqlite+aiosqlite:///"
):
    DATABASE_URL = DATABASE_URL.replace("sqlite:///", "sqlite+aiosqlite:///")

engine = create_async_engine(
    DATABASE_URL,
    echo=settings.DEBUG,
    connect_args={"check_same_thread": False}
    if DATABASE_URL.startswith("sqlite")
    else {},
)

AsyncSessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
)

Base = declarative_base()


async def init_db():
    """Initialize the database creating all tables."""
    # Ensure data directory exists if using local sqlite
    if DATABASE_URL.startswith("sqlite+aiosqlite:///data/"):
        os.makedirs("data", exist_ok=True)

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
