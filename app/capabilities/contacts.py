from app.capabilities import app
from app.domain.models import ContactStatus, ContactSubmission
from app.domain.repositories import ContactRepository


@app.capability(description="Store a contact request from the public landing page.")
async def submit_contact(
    name: str,
    email: str,
    message: str,
    repository: ContactRepository,
    company: str | None = None,
    phone: str | None = None,
    subject: str | None = None,
) -> ContactSubmission:
    # Business validation could go here
    if not name or not email or not message:
        raise ValueError("Name, email, and message are required fields.")

    submission = await repository.create(
        name=name,
        email=email,
        company=company,
        phone=phone,
        subject=subject,
        message=message,
    )
    return submission


@app.capability(description="Retrieve a paginated list of contact submissions.")
async def list_contacts(
    repository: ContactRepository,
    status: ContactStatus | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[ContactSubmission]:
    return await repository.list_all(status=status, limit=limit, offset=offset)


@app.capability(description="Get a single contact submission by ID.")
async def get_contact(
    submission_id: int,
    repository: ContactRepository,
) -> ContactSubmission | None:
    return await repository.get_by_id(submission_id)


@app.capability(description="Update the status of a contact submission.")
async def update_contact_status(
    submission_id: int,
    status: ContactStatus,
    repository: ContactRepository,
) -> ContactSubmission | None:
    return await repository.update_status(submission_id, status)
