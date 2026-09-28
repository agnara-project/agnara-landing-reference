import dataclasses
from datetime import datetime
from typing import Literal

ContactStatus = Literal["new", "reviewed", "archived"]


@dataclasses.dataclass
class ContactSubmission:
    id: int
    name: str
    email: str
    company: str | None
    phone: str | None
    subject: str | None
    message: str
    status: ContactStatus
    created_at: datetime
    updated_at: datetime


@dataclasses.dataclass
class DashboardStats:
    total_submissions: int
    new_submissions: int
    reviewed_submissions: int
    archived_submissions: int
    recent_messages: list[ContactSubmission]
