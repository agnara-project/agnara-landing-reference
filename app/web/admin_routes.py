from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.routing import Route
from starlette.templating import Jinja2Templates

from app.web.auth import requires_auth
from app.web.security import generate_csrf_token, verify_csrf_token

templates = Jinja2Templates(directory="app/templates")


@requires_auth
async def admin_dashboard(request: Request):
    from app.capabilities.admin import dashboard_stats

    # Retrieve stats via capability
    stats = await dashboard_stats()

    return templates.TemplateResponse(request, "admin/dashboard.html", {"stats": stats})


@requires_auth
async def admin_submissions(request: Request):
    status_filter = request.query_params.get("status")
    if status_filter not in ["new", "reviewed", "archived", None, ""]:
        status_filter = None

    page = int(request.query_params.get("page", 1))
    limit = 20
    offset = (page - 1) * limit

    from app.capabilities.contacts import list_contacts

    submissions = await list_contacts(
        status=status_filter if status_filter else None, limit=limit, offset=offset
    )

    return templates.TemplateResponse(
        request,
        "admin/submissions.html",
        {"submissions": submissions, "status_filter": status_filter, "page": page},
    )


@requires_auth
async def admin_submission_detail(request: Request):
    sub_id = int(request.path_params["id"])

    from app.capabilities.contacts import get_contact

    submission = await get_contact(submission_id=sub_id)

    if not submission:
        return HTMLResponse("Not Found", status_code=404)

    csrf_token = generate_csrf_token(request)

    return templates.TemplateResponse(
        request,
        "admin/submission_detail.html",
        {"submission": submission, "csrf_token": csrf_token},
    )


@requires_auth
async def admin_submission_update_status(request: Request):
    sub_id = int(request.path_params["id"])
    form = await request.form()

    # CSRF check
    csrf_token = form.get("csrf_token")
    if not csrf_token or not verify_csrf_token(request, str(csrf_token)):
        return HTMLResponse("Invalid CSRF", status_code=400)

    status = str(form.get("status"))
    if status not in ["new", "reviewed", "archived"]:
        return HTMLResponse("Invalid Status", status_code=400)

    from app.capabilities.contacts import update_contact_status

    await update_contact_status(submission_id=sub_id, status=status)  # type: ignore

    return RedirectResponse(url=f"/admin/submissions/{sub_id}", status_code=303)


routes = [
    Route("/admin", endpoint=admin_dashboard, methods=["GET"]),
    Route("/admin/submissions", endpoint=admin_submissions, methods=["GET"]),
    Route(
        "/admin/submissions/{id:int}", endpoint=admin_submission_detail, methods=["GET"]
    ),
    Route(
        "/admin/submissions/{id:int}/status",
        endpoint=admin_submission_update_status,
        methods=["POST"],
    ),
]
