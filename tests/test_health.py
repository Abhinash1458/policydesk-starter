def test_health(client):
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


def test_seed_data_loaded(client):
    assert len(client.get("/api/products").json()) == 3
    assert len(client.get("/api/customers").json()) == 2


def test_dashboard_renders(client):
    r = client.get("/")
    assert r.status_code == 200
    assert "PolicyDesk" in r.text
