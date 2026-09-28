import pytest
from agnara import AnonymousPrincipal, CapabilityId, Principal
from agnara.execution import (
    CapabilityRuntime,
    ExecutionContext,
    Failure,
    Invocation,
    Success,
)


@pytest.mark.asyncio
async def test_submit_contact_capability_success(test_runtime: CapabilityRuntime):
    context = ExecutionContext(
        Invocation(
            CapabilityId.parse("contacts.submit"),
            {
                "name": "Test User",
                "email": "test@example.com",
                "message": "Hello from tests",
            },
            {},
        ),
        di_container=test_runtime._container,
        principal=AnonymousPrincipal(),
    )

    result = await test_runtime.invoke_result(context)

    assert isinstance(result, Success)
    submission = result.value
    assert submission.name == "Test User"
    assert submission.email == "test@example.com"
    assert submission.message == "Hello from tests"


@pytest.mark.asyncio
async def test_submit_contact_capability_validation(test_runtime: CapabilityRuntime):
    context = ExecutionContext(
        Invocation(
            CapabilityId.parse("contacts.submit"),
            {
                "name": "",  # Empty name should fail
                "email": "test@example.com",
                "message": "Hello",
            },
            {},
        ),
        di_container=test_runtime._container,
        principal=AnonymousPrincipal(),
    )

    result = await test_runtime.invoke_result(context)

    # Should canonical failure
    assert isinstance(result, Failure)
    assert result.code.value == "invalid_input"


@pytest.mark.asyncio
async def test_admin_capabilities_require_scope(test_runtime: CapabilityRuntime):
    # Try to access dashboard anonymously
    context = ExecutionContext(
        Invocation(
            CapabilityId.parse("contacts.dashboard"),
            {},
            {},
        ),
        di_container=test_runtime._container,
        principal=AnonymousPrincipal(),
    )

    result = await test_runtime.invoke_result(context)
    assert isinstance(result, Failure)
    assert (
        result.code.value == "interaction_required" or result.code.value == "forbidden"
    )

    # Now try with proper scopes
    admin_context = ExecutionContext(
        Invocation(
            CapabilityId.parse("contacts.dashboard"),
            {},
            {},
        ),
        di_container=test_runtime._container,
        principal=Principal(identity="admin", scopes={"contacts:read"}),
    )

    result = await test_runtime.invoke_result(admin_context)
    assert isinstance(result, Success)
    assert hasattr(result.value, "total_submissions")
