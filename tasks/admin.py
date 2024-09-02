from django.contrib import admin
from .models import Task, CalendarEvent

@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'priority', 'status', 'due_date', 'created_at', 'updated_at')
    list_filter = ('priority', 'status', 'due_date')
    search_fields = ('title', 'description')

@admin.register(CalendarEvent)
class CalendarEventAdmin(admin.ModelAdmin):
    list_display = ('title', 'user', 'start_time', 'end_time', 'all_day', 'created_at', 'updated_at')
    list_filter = ('start_time', 'end_time', 'all_day')
    search_fields = ('title', 'description')
