import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health_endpoint(client: AsyncClient):
    response = await client.get("/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


@pytest.mark.asyncio
async def test_index_page(client: AsyncClient):
    response = await client.get("/")
    assert response.status_code == 200
    assert "Agnara" in response.text
    assert "<form" in response.text


@pytest.mark.asyncio
async def test_admin_redirect_unauthenticated(client: AsyncClient):
    response = await client.get("/admin")
    assert response.status_code == 303
    assert response.headers["location"] == "/admin/login"
