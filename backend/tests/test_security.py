def test_registration_login_and_authorization(client):
    response = client.post("/api/auth/register", json={"username": "admin", "password": "correct horse battery staple"})
    assert response.status_code == 201
    token = response.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    assert client.get("/api/events", headers=headers).status_code == 200
    assert client.patch("/api/rules/AUTH-001", json={"enabled": False}, headers=headers).status_code == 200
    assert client.post("/api/auth/register", json={"username": "second", "password": "correct horse battery staple"}).status_code == 403
    assert client.post("/api/auth/users", json={"username": "analyst", "password": "correct horse battery staple"}, headers=headers).status_code == 201
    analyst = client.post("/api/auth/login", json={"username": "analyst", "password": "correct horse battery staple"})
    analyst_headers = {"Authorization": f"Bearer {analyst.json()['access_token']}"}
    assert client.patch("/api/rules/AUTH-001", json={"enabled": True}, headers=analyst_headers).status_code == 403


def test_unauthenticated_boundaries(client):
    assert client.get("/api/events").status_code == 401
    assert client.get("/api/rules").status_code == 401
    assert client.get("/api/health").status_code == 200


def test_streaming_ingestion_and_advanced_filter(client):
    registration = client.post("/api/auth/register", json={"username": "operator", "password": "correct horse battery staple"})
    headers = {"Authorization": f"Bearer {registration.json()['access_token']}"}
    payload = b'{"timestamp":"2025-01-01T00:00:00Z","event_type":"login","username":"alice","message":"hello"}\n'
    response = client.post("/api/events/ingest?source=json", files={"file": ("events.jsonl", payload, "application/json")}, headers=headers)
    assert response.status_code == 200 and response.json()["accepted"] == 1
    result = client.get("/api/events?q=hello&username=alice&page_size=1", headers=headers)
    assert result.status_code == 200 and result.json()["total"] == 1
