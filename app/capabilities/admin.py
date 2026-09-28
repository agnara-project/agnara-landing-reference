from app.capabilities import app
from app.domain.models import DashboardStats
from app.domain.repositories import ContactRepository


@app.capability(
    description="Calculate and return dashboard statistics for the admin panel."
)
async def dashboard_stats(repository: ContactRepository) -> DashboardStats:
    total = await repository.count()
    new_count = await repository.count(status="new")
    reviewed_count = await repository.count(status="reviewed")
    archived_count = await repository.count(status="archived")

    # Get the 5 most recent submissions for the dashboard
    recent = await repository.list_all(limit=5)

    return DashboardStats(
        total_submissions=total,
        new_submissions=new_count,
        reviewed_submissions=reviewed_count,
        archived_submissions=archived_count,
        recent_messages=recent,
    )
