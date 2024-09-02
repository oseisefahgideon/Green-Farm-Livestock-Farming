from django.urls import path
from .views import LivestockListCreateView, LivestockRetrieveUpdateDestroyView, FeedingRecordListCreateView, FeedingRecordRetrieveUpdateDestroyView, HealthRecordListCreateView, HealthRecordRetrieveUpdateDestroyView

urlpatterns = [
    path('livestock/', LivestockListCreateView.as_view(), name='livestock-list-create'),
    path('livestock/<uuid:pk>/', LivestockRetrieveUpdateDestroyView.as_view(), name='livestock-detail'),
    path('feeding-records/<uuid:livestock_id>/', FeedingRecordListCreateView.as_view(), name='feeding-record-list-create'),
    path('feeding-records/<uuid:livestock_id>/<uuid:pk>/', FeedingRecordRetrieveUpdateDestroyView.as_view(), name='feeding-record-detail'),
    path('livestock/<uuid:livestock_id>/health-records/', HealthRecordListCreateView.as_view(), name='healthrecord-list-create'),
    path('livestock/<uuid:livestock_id>/health-records/<uuid:pk>/', HealthRecordRetrieveUpdateDestroyView.as_view(), name='healthrecord-retrieve-update-destroy'),

]
