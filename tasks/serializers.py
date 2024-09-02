from rest_framework import serializers
from .models import Task, CalendarEvent

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        exclude = ['is_deleted']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']

class CalendarEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = CalendarEvent
        exclude = ['is_deleted']
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']
