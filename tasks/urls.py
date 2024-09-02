from django.urls import path
from .views import (
    TaskListCreateView,
    TaskRetrieveUpdateDestroyView,
    CalendarEventListCreateView,
    CalendarEventRetrieveUpdateDestroyView
)

urlpatterns = [
    path('tasks/', TaskListCreateView.as_view(), name='task-list-create'),
    path('tasks/<uuid:pk>/', TaskRetrieveUpdateDestroyView.as_view(), name='task-retrieve-update-destroy'),
    path('calendar-events/', CalendarEventListCreateView.as_view(), name='calendar-event-list-create'),
    path('calendar-events/<uuid:pk>/', CalendarEventRetrieveUpdateDestroyView.as_view(), name='calendar-event-retrieve-update-destroy'),
]
