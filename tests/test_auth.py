

def test_request_without_api_key_is_rejected(client):
    del client.headers["X-API-Key"]

    response = client.get("/projects")

    assert response.status_code == 401


def test_request_with_wrong_api_key_is_rejected(client):
    response = client.get("/projects", headers={"X-API-Key": "wrong-key"})

    assert response.status_code == 401


def test_request_with_valid_api_key_is_accepted(client):
    response = client.get("/projects")

    assert response.status_code == 200


def test_health_does_not_require_api_key(client):
    del client.headers["X-API-Key"]

    response = client.get("/health")

    assert response.status_code == 200