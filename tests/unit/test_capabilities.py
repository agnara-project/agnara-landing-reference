from datetime import UTC, datetime

import pytest

from app.capabilities.contacts import submit_contact
from app.domain.models import ContactSubmission


class MockRepository:
    def __init__(self):
        self.submissions = []
        self.counter = 1

    async def create(
        self, name, email, message, company=None, phone=None, subject=None
    ):
        sub = ContactSubmission(
            id=self.counter,
            name=name,
            email=email,
            company=company,
            phone=phone,
            subject=subject,
            message=message,
            status="new",
            created_at=datetime.now(UTC),
            updated_at=datetime.now(UTC),
        )
        self.submissions.append(sub)
        self.counter += 1
        return sub

    async def list_all(self, status=None, limit=50, offset=0):
        if status:
            return [s for s in self.submissions if s.status == status][
                offset : offset + limit
            ]
        return self.submissions[offset : offset + limit]


@pytest.mark.asyncio
async def test_submit_contact_capability_success():
    repo = MockRepository()
    result = await submit_contact(
        name="Test User", email="test@example.com", message="Hello", repository=repo
    )

    assert result.name == "Test User"
    assert result.email == "test@example.com"
    assert len(repo.submissions) == 1


@pytest.mark.asyncio
async def test_submit_contact_capability_validation():
    repo = MockRepository()
    with pytest.raises(ValueError):
        await submit_contact(
            name="", email="test@example.com", message="Hello", repository=repo
        )
