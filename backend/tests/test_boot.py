import pytest

def test_health_check_returns_200(client):
    """Ensure the application boots and health check works."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}
