from rest_framework import serializers
from .models import Project, Task


class TaskSerializer(serializers.ModelSerializer):
    project_name = serializers.CharField(source="project.name", read_only=True)
    assignee_username = serializers.CharField(source="assignee.username",
                                              read_only=True, default=None)

    class Meta:
        model = Task
        fields = ["id", "project", "project_name", "title", "status",
                  "assignee", "assignee_username", "due_date", "created_at"]
        read_only_fields = ["created_at"]

    def validate_title(self, value):
        if len(value.strip()) < 3:
            raise serializers.ValidationError("Title must be at least 3 characters.")
        return value.strip()

    def validate_project(self, value):
        if value.owner_id != self.context["request"].user.id:
            raise serializers.ValidationError("You can only add tasks to your own projects.")
        return value

    def validate(self, attrs):
        status = attrs.get("status", getattr(self.instance, "status", None))
        assignee = attrs.get("assignee", getattr(self.instance, "assignee", None))
        if status == Task.Status.DONE and assignee is None:
            raise serializers.ValidationError("A done task needs an assignee.")
        return attrs


class ProjectSerializer(serializers.ModelSerializer):
    task_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Project
        fields = ["id", "name", "owner", "task_count", "created_at"]
        read_only_fields = ["owner", "created_at"]