from django.urls import path
from .views import (
    TransactionListCreateView,
    TransactionRetrieveUpdateDestroyView,
    TransactionSummaryView,
)

urlpatterns = [
    path('transactions/', TransactionListCreateView.as_view(), name='transaction-list-create'),
    path('transactions/<uuid:pk>/', TransactionRetrieveUpdateDestroyView.as_view(), name='transaction-detail'),
    path('summary/', TransactionSummaryView.as_view(), name='transaction-summary'),
]
