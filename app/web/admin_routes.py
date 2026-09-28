from agnara import Principal
from agnara.execution import Failure
from starlette.requests import Request
from starlette.responses import HTMLResponse, RedirectResponse
from starlette.routing import Route
from starlette.templating import Jinja2Templates

from app.runtime import invoke_capability
from app.web.auth import requires_auth
from app.web.security import generate_csrf_token, verify_csrf_token

templates = Jinja2Templates(directory="app/templates")


def get_admin_principal(request: Request) -> Principal:
    # We map the Starlette authenticated session to an Agnara Principal
    # We assign the required scopes for admin capabilities.
    return Principal(
        identity=request.session.get("admin", "admin"),
        scopes={"contacts:read", "contacts:write"},
    )


@requires_auth
async def admin_dashboard(request: Request):
    runtime = request.app.state.agnara_runtime
    principal = get_admin_principal(request)

    result = await invoke_capability(
        runtime, "contacts.dashboard", {}, principal=principal
    )
    if isinstance(result, Failure):
        return HTMLResponse(f"Error: {result.message}", status_code=500)

    stats = result.value

    return templates.TemplateResponse(request, "admin/dashboard.html", {"stats": stats})


@requires_auth
async def admin_submissions(request: Request):
    status_filter = request.query_params.get("status")
    if status_filter not in ["new", "reviewed", "archived", None, ""]:
        status_filter = None

    page = int(request.query_params.get("page", 1))
    limit = 20
    offset = (page - 1) * limit

    runtime = request.app.state.agnara_runtime
    principal = get_admin_principal(request)

    payload = {
        "status": status_filter if status_filter else None,
        "limit": limit,
        "offset": offset,
    }

    result = await invoke_capability(
        runtime, "contacts.list", payload, principal=principal
    )
    if isinstance(result, Failure):
        return HTMLResponse(f"Error: {result.message}", status_code=500)

    submissions = result.value

    return templates.TemplateResponse(
        request,
        "admin/submissions.html",
        {"submissions": submissions, "status_filter": status_filter, "page": page},
    )


@requires_auth
async def admin_submission_detail(request: Request):
    sub_id = int(request.path_params["id"])

    runtime = request.app.state.agnara_runtime
    principal = get_admin_principal(request)

    result = await invoke_capability(
        runtime, "contacts.get", {"submission_id": sub_id}, principal=principal
    )

    if isinstance(result, Failure):
        return HTMLResponse(f"Error: {result.message}", status_code=500)

    submission = result.value
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

    runtime = request.app.state.agnara_runtime
    principal = get_admin_principal(request)

    payload = {"submission_id": sub_id, "status": status}

    result = await invoke_capability(
        runtime, "contacts.update_status", payload, principal=principal
    )
    if isinstance(result, Failure):
        return HTMLResponse(f"Error: {result.message}", status_code=500)

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
