

PROJECT = {
    "name": "Elektro-SUV 2028",
    "start_date": "2026-01-01",
    "end_date": "2027-12-31",
}


def test_create_project(client):
    response = client.post("/projects", json=PROJECT)

    assert response.status_code == 201
    assert response.json()["name"] == "Elektro-SUV 2028"


def test_create_project_with_end_before_start_fails(client):
    response = client.post("/projects", json={**PROJECT, "end_date": "2025-12-31"})

    assert response.status_code == 422


def test_list_projects(client):
    client.post("/projects", json=PROJECT)
    client.post("/projects", json={**PROJECT, "name": "Kompaktwagen"})

    response = client.get("/projects")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_get_unknown_project_returns_404(client):
    response = client.get("/projects/999")

    assert response.status_code == 404


def test_update_project(client):
    project_id = client.post("/projects", json=PROJECT).json()["id"]

    response = client.patch(f"/projects/{project_id}", json={"name": "Elektro-SUV 2029"})

    assert response.status_code == 200
    assert response.json()["name"] == "Elektro-SUV 2029"


def test_update_with_end_before_start_fails(client):
    project_id = client.post("/projects", json=PROJECT).json()["id"]

    response = client.patch(f"/projects/{project_id}", json={"end_date": "2025-01-01"})

    assert response.status_code == 422


def test_delete_project(client):
    project_id = client.post("/projects", json=PROJECT).json()["id"]

    response = client.delete(f"/projects/{project_id}")

    assert response.status_code == 204
    assert client.get(f"/projects/{project_id}").status_code == 404