from django.db.models import Count
from django.utils.dateparse import parse_date
from rest_framework import viewsets, permissions, filters
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from .models import Project, Task
from .serializers import ProjectSerializer, TaskSerializer
from .permissions import IsProjectOwner
from .services import project_stats
import logging
from django.db import transaction
from .jobs import notify_assignee

logger = logging.getLogger(__name__)

class ProjectViewSet(viewsets.ModelViewSet):
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectOwner]

    def get_queryset(self):
        return (Project.objects.filter(owner=self.request.user)
                .annotate(task_count=Count("tasks")))

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["get"])
    def stats(self, request, pk=None):
        project = self.get_object()  # ownership check happens here, before the cache
        return Response(project_stats(project.id))

class TaskViewSet(viewsets.ModelViewSet):
    serializer_class = TaskSerializer
    permission_classes = [permissions.IsAuthenticated, IsProjectOwner]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["title"]
    ordering_fields = ["due_date", "created_at"]

    def perform_create(self, serializer):
        task = serializer.save()
        if task.assignee_id:
            transaction.on_commit(lambda: self._enqueue_notify(task.id))

    @staticmethod
    def _enqueue_notify(task_id):
        try:
            notify_assignee.delay(task_id)  # pass the ID, not the object
        except Exception:
            logger.exception("could not enqueue notify_assignee for task %s", task_id)

    def get_queryset(self):
        qs = (Task.objects.filter(project__owner=self.request.user)
              .select_related("project", "assignee"))
        params = self.request.query_params

        status = params.get("status")
        if status:
            qs = qs.filter(status=status)

        project = params.get("project")
        if project:
            qs = qs.filter(project_id=project)

        due_before = params.get("due_before")
        if due_before:
            try:
                d = parse_date(due_before)
            except ValueError:
                d = None
            if d is None:
                raise ValidationError({"due_before": "Use the format YYYY-MM-DD."})
            qs = qs.filter(due_date__lt=d)

        return qs

    @action(detail=True, methods=["post"])
    def complete(self, request, pk=None):
        task = self.get_object()
        serializer = self.get_serializer(task, data={"status": Task.Status.DONE}, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)