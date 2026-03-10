from rest_framework import serializers
from .models import Transaction


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        exclude = ['is_deleted']
        read_only_fields = ['id', 'created_at', 'updated_at', 'farm', 'user']


class TransactionSummarySerializer(serializers.Serializer):
    """Used for monthly and category summary endpoints."""
    total_income = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=12, decimal_places=2)
    net_profit = serializers.DecimalField(max_digits=12, decimal_places=2)
    transaction_count = serializers.IntegerField()
