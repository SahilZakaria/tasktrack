import pytest
from django.core.cache import cache


@pytest.fixture(autouse=True)
def locmem_cache(settings):
    settings.CACHES = {"default": {"BACKEND": "django.core.cache.backends.locmem.LocMemCache"}}
    cache.clear()


@pytest.mark.django_db
def test_health_ok_without_login(client):
    resp = client.get("/api/health/")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "db": "ok", "cache": "ok"}


@pytest.mark.django_db
def test_request_id_generated(client):
    resp = client.get("/api/health/")
    assert len(resp["X-Request-ID"]) == 12


@pytest.mark.django_db
@pytest.mark.parametrize("sent, echoed", [("abc-123", True), ("bad id!", False)])
def test_request_id_header_validated(client, sent, echoed):
    resp = client.get("/api/health/", HTTP_X_REQUEST_ID=sent)
    assert (resp["X-Request-ID"] == sent) is echoed