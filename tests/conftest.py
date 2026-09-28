import os

os.environ["APP_ENV"] = "development"

from collections.abc import AsyncGenerator

import pytest
from agnara.core.di import DIContainer
from agnara.di import DIRegistry, provider
from agnara.execution import CapabilityRuntime, ExecutionPlan
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.apps.contacts.ports import ContactRepository
from app.infrastructure.persistence.database import Base
from app.infrastructure.persistence.repositories import SqlAlchemyContactRepository
from app.main import app, project

# Use an in-memory SQLite database for testing
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"


@pytest.fixture
async def engine():
    engine = create_async_engine(TEST_DATABASE_URL, echo=False)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await engine.dispose()


@pytest.fixture
def session_factory(engine):
    return async_sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)


@pytest.fixture
def repository(session_factory) -> SqlAlchemyContactRepository:
    return SqlAlchemyContactRepository(session_factory)


@pytest.fixture
async def test_runtime(repository):
    capabilities = project.compile()

    dependencies = DIRegistry()

    @provider()
    def provide_repo() -> ContactRepository:
        return repository

    dependencies.bind(ContactRepository, provide_repo)

    plans = tuple(
        ExecutionPlan.compile(
            capabilities[capability_id],
            dependencies,
        )
        for capability_id in capabilities
    )

    container = DIContainer(dependencies)
    runtime = CapabilityRuntime(
        capabilities,
        plans,
        container,
    )

    yield runtime

    await runtime.aclose()
    await container.aclose()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as client:
        yield client
