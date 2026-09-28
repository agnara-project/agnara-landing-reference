from typing import Any

from agnara import (
    AnonymousPrincipal,
    CapabilityId,
    Principal,
)
from agnara.execution import CapabilityRuntime, ExecutionContext, Invocation


async def invoke_capability(
    runtime: CapabilityRuntime,
    capability_id: str,
    payload: dict[str, Any],
    principal: Principal | AnonymousPrincipal | None = None,
) -> Any:
    """
    Execute an Agnara capability natively through the runtime.
    This bridge adapts the host's plain dictionaries into the Agnara invocation format.
    """
    if principal is None:
        principal = AnonymousPrincipal()

    # ADR 0094: We wrap the host input into an Agnara Invocation
    context = ExecutionContext(
        Invocation(
            CapabilityId.parse(capability_id),
            payload,
            {},  # No explicit bindings from direct invocation
        ),
        di_container=runtime._container,  # Need DI container reference
        principal=principal,
    )

    # Runtime handles ExecutionPlan, DI, policies
    return await runtime.invoke_result(context)
