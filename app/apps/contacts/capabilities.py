from agnara import Risk, StandardEffect, ValidationError

from .app import app
from .models import ContactStatus, ContactSubmission, DashboardStats
from .ports import ContactRepository


@app.capability(
    name="submit",
    description="Receive and persist a public contact request.",
    effects=(StandardEffect.DATABASE_WRITE,),
    risk=Risk.LOW,
    idempotent=False,
)
async def submit_contact(
    name: str,
    email: str,
    message: str,
    repository: ContactRepository,
    company: str | None = None,
    phone: str | None = None,
    subject: str | None = None,
) -> ContactSubmission:
    # Business validation using Agnara mechanisms
    if not name.strip():
        raise ValidationError("Name is required", path=("name",))
    if not email.strip() or "@" not in email:
        raise ValidationError("Valid email is required", path=("email",))
    if not message.strip():
        raise ValidationError("Message is required", path=("message",))

    submission = await repository.create(
        name=name.strip(),
        email=email.strip(),
        company=company.strip() if company else None,
        phone=phone.strip() if phone else None,
        subject=subject.strip() if subject else None,
        message=message.strip(),
    )
    return submission


@app.capability(
    name="list",
    description="Retrieve a paginated list of contact submissions.",
    effects=(StandardEffect.READ,),
    risk=Risk.LOW,
    scopes=("contacts:read",),
    idempotent=True,
)
async def list_contacts(
    repository: ContactRepository,
    status: ContactStatus | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[ContactSubmission]:
    return await repository.list_all(status=status, limit=limit, offset=offset)


@app.capability(
    name="get",
    description="Get a single contact submission by ID.",
    effects=(StandardEffect.READ,),
    risk=Risk.LOW,
    scopes=("contacts:read",),
    idempotent=True,
)
async def get_contact(
    submission_id: int,
    repository: ContactRepository,
) -> ContactSubmission | None:
    return await repository.get_by_id(submission_id)


@app.capability(
    name="update_status",
    description="Update the status of a contact submission.",
    effects=(StandardEffect.DATABASE_WRITE,),
    risk=Risk.MEDIUM,
    scopes=("contacts:write",),
    idempotent=True,  # Setting same status repeatedly is idempotent
)
async def update_contact_status(
    submission_id: int,
    status: ContactStatus,
    repository: ContactRepository,
) -> ContactSubmission | None:
    return await repository.update_status(submission_id, status)


@app.capability(
    name="dashboard",
    description="Calculate and return dashboard statistics for the admin panel.",
    effects=(StandardEffect.READ,),
    risk=Risk.LOW,
    scopes=("contacts:read",),
    idempotent=True,
)
async def dashboard_stats(repository: ContactRepository) -> DashboardStats:
    total = await repository.count()
    new_count = await repository.count(status="new")
    reviewed_count = await repository.count(status="reviewed")
    archived_count = await repository.count(status="archived")

    recent = await repository.list_all(limit=5)

    return DashboardStats(
        total_submissions=total,
        new_submissions=new_count,
        reviewed_submissions=reviewed_count,
        archived_submissions=archived_count,
        recent_messages=recent,
    )
