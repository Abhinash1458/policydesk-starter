"""Smoke tests — two fast checks that the app boots and serves. CI runs these first; if they fail nothing else runs."""
import pytest

pytestmark = pytest.mark.smoke


def test_health_endpoint_is_alive(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_home_page_serves_html(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.headers["content-type"].startswith("text/html")
    assert "PolicyDesk" in r.text
