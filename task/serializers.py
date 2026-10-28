from .models import Task
from rest_framework.serializers import ModelSerializer

class TaskSerializers(ModelSerializer):
    class Meta:
        model = Task
        fields = [
            'id',
            'title',
            'description',
            'assignTo',
            'assigneeToId',
            'assigneeBy',
            'assigneeById',
            'dueDate',
            'priority',
            'notes',
            'status',
            'updated_at',
            'created_at'
        ]
