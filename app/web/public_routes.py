from agnara.execution import Failure
from starlette.requests import Request
from starlette.responses import JSONResponse, RedirectResponse
from starlette.routing import Route
from starlette.templating import Jinja2Templates

from app.runtime import invoke_capability
from app.web.security import generate_csrf_token, verify_csrf_token

templates = Jinja2Templates(directory="app/templates")


async def index(request: Request):
    csrf_token = generate_csrf_token(request)
    return templates.TemplateResponse(request, "index.html", {"csrf_token": csrf_token})


async def contact_post(request: Request):
    form = await request.form()

    # Security: Honeypot check
    if form.get("website_url"):
        return JSONResponse(
            {"status": "success", "message": "Message sent."}, status_code=200
        )

    # Security: CSRF verification
    csrf_token = form.get("csrf_token")
    if not csrf_token or not verify_csrf_token(request, str(csrf_token)):
        return JSONResponse(
            {"status": "error", "message": "Invalid CSRF token."}, status_code=400
        )

    # Extract fields
    payload = {
        "name": str(form.get("name", "")),
        "email": str(form.get("email", "")),
        "message": str(form.get("message", "")),
        "company": str(form.get("company", "")) if form.get("company") else None,
        "phone": str(form.get("phone", "")) if form.get("phone") else None,
        "subject": str(form.get("subject", "")) if form.get("subject") else None,
    }

    # Execute capability through Agnara Runtime
    runtime = request.app.state.agnara_runtime
    result = await invoke_capability(runtime, "contacts.submit", payload)

    is_json = (
        request.headers.get("accept") == "application/json"
        or request.headers.get("X-Requested-With") == "XMLHttpRequest"
    )

    if isinstance(result, Failure):
        error_msg = result.message
        if is_json:
            return JSONResponse(
                {"status": "error", "message": error_msg}, status_code=400
            )
        return RedirectResponse(url=f"/?error={error_msg}", status_code=303)

    # Success
    if is_json:
        return JSONResponse(
            {"status": "success", "message": "Your message has been sent successfully!"}
        )

    return RedirectResponse(url="/?success=1", status_code=303)


routes = [
    Route("/", endpoint=index, methods=["GET"]),
    Route("/contact", endpoint=contact_post, methods=["POST"]),
]
