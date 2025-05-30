import pytest
from httpx import AsyncClient
from main import app

@pytest.mark.asyncio
async def test_signup_and_verify_email():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/signup", data={
            "name": "Test User",
            "email": "testuser@example.com",
            "password": "test123",
            "role": "client"
        })
        assert response.status_code == 200
        verify_url = response.json()["verify_url"]
        
        # Extract encrypted part and verify email
        encrypted = verify_url.split("/")[-1]
        verify_res = await ac.get(f"/verify-email/{encrypted}")
        assert verify_res.status_code == 200

@pytest.mark.asyncio
async def test_signin():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.post("/signin", json={
            "email": "testuser@example.com",
            "password": "test123"
        })
        assert response.status_code == 200
        assert "access_token" in response.json()
