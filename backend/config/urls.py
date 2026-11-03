from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from config.health import health
from tasks.views import ProjectViewSet, TaskViewSet

router = DefaultRouter()
router.register("projects", ProjectViewSet, basename="project")
router.register("tasks", TaskViewSet, basename="task")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/health/", health),
    path("api/", include(router.urls)),
    path("api/auth/", include("rest_framework.urls")),
]