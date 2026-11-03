from datetime import date

import pytest
from django.contrib.auth.models import User
from rest_framework.test import APIClient

from tasks.models import Project, Task


@pytest.fixture
def user(db):
    return User.objects.create_user("ana", password="pw-12345")


@pytest.fixture
def client(user):
    c = APIClient()
    c.force_authenticate(user=user)
    return c


@pytest.fixture
def project(user):
    return Project.objects.create(name="Launch", owner=user)


def test_requires_login(db):
    resp = APIClient().get("/api/tasks/")
    assert resp.status_code in (401, 403)


def test_create_task(client, project):
    resp = client.post("/api/tasks/", {"project": project.id, "title": "Write docs"},
                       format="json")
    assert resp.status_code == 201
    assert Task.objects.filter(title="Write docs").exists()


def test_rejects_short_title(client, project):
    resp = client.post("/api/tasks/", {"project": project.id, "title": "x"}, format="json")
    assert resp.status_code == 400
    assert "title" in resp.json()


def test_cannot_see_other_users_tasks(client, db):
    other = User.objects.create_user("bob")
    p = Project.objects.create(name="Secret", owner=other)
    Task.objects.create(project=p, title="Hidden task")
    resp = client.get("/api/tasks/")
    assert resp.json()["count"] == 0


def test_cannot_add_task_to_other_users_project(client, db):
    other = User.objects.create_user("bob")
    p = Project.objects.create(name="Secret", owner=other)
    resp = client.post("/api/tasks/", {"project": p.id, "title": "Sneaky"}, format="json")
    assert resp.status_code == 400


def test_task_list_query_count(client, project, django_assert_max_num_queries):
    for i in range(30):
        Task.objects.create(project=project, title=f"Task {i}")
    with django_assert_max_num_queries(5):
        client.get("/api/tasks/")

def test_complete_action(client, user, project):
    task = Task.objects.create(project=project, title="Ship it", assignee=user)
    resp = client.post(f"/api/tasks/{task.id}/complete/")
    assert resp.status_code == 200
    task.refresh_from_db()
    assert task.status == "done"


def test_complete_requires_assignee(client, project):
    task = Task.objects.create(project=project, title="Nobody owns this")
    resp = client.post(f"/api/tasks/{task.id}/complete/")
    assert resp.status_code == 400


def test_due_before_filter(client, project):
    Task.objects.create(project=project, title="Early", due_date=date(2026, 10, 1))
    Task.objects.create(project=project, title="Late", due_date=date(2026, 12, 1))
    resp = client.get("/api/tasks/?due_before=2026-11-01")
    titles = [t["title"] for t in resp.json()["results"]]
    assert titles == ["Early"]


def test_due_before_rejects_bad_date(client, db):
    resp = client.get("/api/tasks/?due_before=banana")
    assert resp.status_code == 400


def test_cannot_delete_other_users_task(client, db):
    other = User.objects.create_user("bob")
    p = Project.objects.create(name="Secret", owner=other)
    t = Task.objects.create(project=p, title="Bob's task")
    resp = client.delete(f"/api/tasks/{t.id}/")
    assert resp.status_code == 404
    assert Task.objects.filter(pk=t.id).exists()