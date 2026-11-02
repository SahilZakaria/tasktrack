import pytest
from django.contrib.auth.models import User
from django.core.cache import cache

from tasks.models import Project, Task
from tasks.services import project_stats


@pytest.fixture(autouse=True)
def locmem_cache(settings):
    settings.CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
    cache.clear()


@pytest.mark.django_db
def test_stats_cached_then_invalidated(django_assert_num_queries):
    user = User.objects.create_user("bob", password="x")
    project = Project.objects.create(name="P", owner=user)
    Task.objects.create(project=project, title="one")

    assert project_stats(project.id) == {"todo": 1}
    with django_assert_num_queries(0):
        assert project_stats(project.id) == {"todo": 1}  # served from cache

    Task.objects.create(project=project, title="two")  # signal clears the key
    assert project_stats(project.id) == {"todo": 2}