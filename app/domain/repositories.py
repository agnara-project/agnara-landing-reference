from typing import Protocol

from app.domain.models import ContactStatus, ContactSubmission


class ContactRepository(Protocol):
    async def create(
        self,
        name: str,
        email: str,
        company: str | None,
        phone: str | None,
        subject: str | None,
        message: str,
    ) -> ContactSubmission:
        """Create a new contact submission."""
        ...

    async def get_by_id(self, submission_id: int) -> ContactSubmission | None:
        """Get a contact submission by its ID."""
        ...

    async def list_all(
        self, status: ContactStatus | None = None, limit: int = 50, offset: int = 0
    ) -> list[ContactSubmission]:
        """List contact submissions, optionally filtered by status."""
        ...

    async def count(self, status: ContactStatus | None = None) -> int:
        """Count total submissions, optionally filtered by status."""
        ...

    async def update_status(
        self, submission_id: int, status: ContactStatus
    ) -> ContactSubmission | None:
        """Update the status of a contact submission."""
        ...
