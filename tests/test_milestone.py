

PROJECT = {
    "name": "Testprojekt",
    "start_date": "2020-01-01",
    "end_date": "2099-12-31",
}


def create_project(client):
    return client.post("/projects", json=PROJECT).json()["id"]


def create_milestone(client, project_id, **fields):
    data = {"title": "Crashtest", "due_date": "2050-06-01", **fields}
    return client.post(f"/projects/{project_id}/milestones", json=data)


def test_create_milestone_defaults_to_planned(client):
    project_id = create_project(client)

    response = create_milestone(client, project_id)

    assert response.status_code == 201
    assert response.json()["status"] == "planned"


def test_create_milestone_for_unknown_project_returns_404(client):
    response = create_milestone(client, 999)

    assert response.status_code == 404


def test_due_date_outside_project_fails(client):
    project_id = create_project(client)

    response = create_milestone(client, project_id, due_date="2019-12-31")

    assert response.status_code == 422


def test_invalid_status_fails(client):
    project_id = create_project(client)

    response = create_milestone(client, project_id, status="fertig")

    assert response.status_code == 422


def test_list_milestones_of_project(client):
    project_id = create_project(client)
    create_milestone(client, project_id, title="Konzept")
    create_milestone(client, project_id, title="Prototyp")

    response = client.get(f"/projects/{project_id}/milestones")

    assert response.status_code == 200
    assert len(response.json()) == 2


def test_update_status(client):
    project_id = create_project(client)
    milestone_id = create_milestone(client, project_id).json()["id"]

    response = client.patch(f"/milestones/{milestone_id}", json={"status": "in_progress"})

    assert response.status_code == 200
    assert response.json()["status"] == "in_progress"


def test_update_due_date_outside_project_fails(client):
    project_id = create_project(client)
    milestone_id = create_milestone(client, project_id).json()["id"]

    response = client.patch(f"/milestones/{milestone_id}", json={"due_date": "2100-01-01"})

    assert response.status_code == 422


def test_delete_milestone(client):
    project_id = create_project(client)
    milestone_id = create_milestone(client, project_id).json()["id"]

    response = client.delete(f"/milestones/{milestone_id}")

    assert response.status_code == 204
    assert client.get(f"/milestones/{milestone_id}").status_code == 404


def test_overdue_returns_only_open_milestones_in_the_past(client):
    project_id = create_project(client)
    create_milestone(client, project_id, title="Überfällig", due_date="2021-01-01")
    create_milestone(client, project_id, title="Erledigt", due_date="2021-01-01", status="done")
    create_milestone(client, project_id, title="Zukunft", due_date="2098-01-01")

    response = client.get("/milestones/overdue")

    titles = [m["title"] for m in response.json()]
    assert titles == ["Überfällig"]


def test_deleting_project_deletes_its_milestones(client):
    project_id = create_project(client)
    milestone_id = create_milestone(client, project_id).json()["id"]

    client.delete(f"/projects/{project_id}")

    assert client.get(f"/milestones/{milestone_id}").status_code == 404