import logging

from celery import shared_task
from django.core.mail import send_mail

from .models import Task

logger = logging.getLogger(__name__)


@shared_task(bind=True, autoretry_for=(ConnectionError,), retry_backoff=True, max_retries=5)
def notify_assignee(self, task_id):
    task = Task.objects.select_related("assignee").filter(pk=task_id).first()
    if task is None or task.assignee is None or not task.assignee.email:
        logger.info("notify_assignee: nothing to do for task %s", task_id)
        return
    send_mail(
        "New task",
        f"You were assigned: {task.title}",
        "noreply@tasktrack.dev",
        [task.assignee.email],
    )