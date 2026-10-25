

from app.rate_limit import RateLimiter


def test_blocks_after_too_many_failed_attempts(client):
    for _ in range(5):
        response = client.get("/projects", headers={"X-API-Key": "wrong-key"})
        assert response.status_code == 401

    response = client.get("/projects", headers={"X-API-Key": "wrong-key"})

    assert response.status_code == 429
    assert "Retry-After" in response.headers


def test_blocked_client_is_rejected_even_with_valid_key(client):
    for _ in range(5):
        client.get("/projects", headers={"X-API-Key": "wrong-key"})

    response = client.get("/projects")

    assert response.status_code == 429


def test_successful_requests_are_not_counted(client):
    for _ in range(10):
        response = client.get("/projects")
        assert response.status_code == 200


def test_attempts_expire_after_window(monkeypatch):
    now = [1000.0]
    monkeypatch.setattr("app.rate_limit.time.monotonic", lambda: now[0])
    limiter = RateLimiter(max_attempts=2, window_seconds=60)

    limiter.register("1.2.3.4")
    limiter.register("1.2.3.4")
    assert limiter.is_blocked("1.2.3.4")

    now[0] += 61
    assert not limiter.is_blocked("1.2.3.4")


def test_clients_are_tracked_separately():
    limiter = RateLimiter(max_attempts=1, window_seconds=60)

    limiter.register("1.1.1.1")

    assert limiter.is_blocked("1.1.1.1")
    assert not limiter.is_blocked("2.2.2.2")