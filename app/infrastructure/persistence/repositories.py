from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from app.apps.contacts.models import ContactStatus, ContactSubmission
from app.apps.contacts.ports import ContactRepository
from app.infrastructure.persistence.models import ContactSubmissionModel


class SqlAlchemyContactRepository(ContactRepository):
    def __init__(self, session_factory: async_sessionmaker[AsyncSession]):
        self.session_factory = session_factory

    def _to_domain(self, model: ContactSubmissionModel) -> ContactSubmission:
        return ContactSubmission(
            id=model.id,
            name=model.name,
            email=model.email,
            company=model.company,
            phone=model.phone,
            subject=model.subject,
            message=model.message,
            status=model.status,  # type: ignore
            created_at=model.created_at,
            updated_at=model.updated_at,
        )

    async def create(
        self,
        name: str,
        email: str,
        company: str | None,
        phone: str | None,
        subject: str | None,
        message: str,
    ) -> ContactSubmission:
        async with self.session_factory() as session:
            new_submission = ContactSubmissionModel(
                name=name,
                email=email,
                company=company,
                phone=phone,
                subject=subject,
                message=message,
                status="new",
            )
            session.add(new_submission)
            await session.commit()
            await session.refresh(new_submission)
            return self._to_domain(new_submission)

    async def get_by_id(self, submission_id: int) -> ContactSubmission | None:
        async with self.session_factory() as session:
            result = await session.execute(
                select(ContactSubmissionModel).where(
                    ContactSubmissionModel.id == submission_id
                )
            )
            model = result.scalar_one_or_none()
            if model:
                return self._to_domain(model)
            return None

    async def list_all(
        self, status: ContactStatus | None = None, limit: int = 50, offset: int = 0
    ) -> list[ContactSubmission]:
        async with self.session_factory() as session:
            query = select(ContactSubmissionModel).order_by(
                ContactSubmissionModel.created_at.desc()
            )
            if status:
                query = query.where(ContactSubmissionModel.status == status)

            query = query.limit(limit).offset(offset)
            result = await session.execute(query)
            models = result.scalars().all()
            return [self._to_domain(m) for m in models]

    async def count(self, status: ContactStatus | None = None) -> int:
        async with self.session_factory() as session:
            query = select(func.count()).select_from(ContactSubmissionModel)
            if status:
                query = query.where(ContactSubmissionModel.status == status)
            result = await session.execute(query)
            return result.scalar_one()

    async def update_status(
        self, submission_id: int, status: ContactStatus
    ) -> ContactSubmission | None:
        async with self.session_factory() as session:
            result = await session.execute(
                select(ContactSubmissionModel).where(
                    ContactSubmissionModel.id == submission_id
                )
            )
            model = result.scalar_one_or_none()
            if model:
                model.status = status
                await session.commit()
                await session.refresh(model)
                return self._to_domain(model)
            return None
