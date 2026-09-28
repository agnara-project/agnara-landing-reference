import pytest

from app.infrastructure.repositories import SqlAlchemyContactRepository


@pytest.mark.asyncio
async def test_create_and_get_submission(repository: SqlAlchemyContactRepository):
    # Test Create
    sub = await repository.create(
        name="Integration Test",
        email="int@test.com",
        company=None,
        phone=None,
        subject=None,
        message="Integration message",
    )

    assert sub.id is not None
    assert sub.status == "new"

    # Test Get
    retrieved = await repository.get_by_id(sub.id)
    assert retrieved is not None
    assert retrieved.name == "Integration Test"


@pytest.mark.asyncio
async def test_update_status(repository: SqlAlchemyContactRepository):
    sub = await repository.create(
        name="Status Test",
        email="status@test.com",
        company=None,
        phone=None,
        subject=None,
        message="msg",
    )

    updated = await repository.update_status(sub.id, "reviewed")
    assert updated is not None
    assert updated.status == "reviewed"

    # Verify via count
    count = await repository.count(status="reviewed")
    assert count == 1
