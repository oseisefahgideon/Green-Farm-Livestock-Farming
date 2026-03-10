from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django.db.models import Sum, Q
from django.db.models.functions import TruncMonth
from decimal import Decimal

from account.models import Farm
from .models import Transaction
from .serializers import TransactionSerializer


def get_user_farm(user):
    return Farm.objects.get(user=user)


class TransactionListCreateView(generics.ListCreateAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        farm = get_user_farm(self.request.user)
        qs = Transaction.objects.filter(farm=farm, is_deleted=False)

        # Optional filters via query params
        tx_type = self.request.query_params.get('type')
        month = self.request.query_params.get('month')   # format: YYYY-MM
        category = self.request.query_params.get('category')

        if tx_type:
            qs = qs.filter(type=tx_type)
        if month:
            try:
                year, mo = month.split('-')
                qs = qs.filter(date__year=year, date__month=mo)
            except ValueError:
                pass
        if category:
            qs = qs.filter(category=category)

        return qs

    def perform_create(self, serializer):
        farm = get_user_farm(self.request.user)
        serializer.save(farm=farm, user=self.request.user)


class TransactionRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = TransactionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        farm = get_user_farm(self.request.user)
        return Transaction.objects.filter(farm=farm, is_deleted=False)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_deleted = True
        instance.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TransactionSummaryView(APIView):
    """
    GET /api/financial/summary/
    Returns overall totals + last 12 months breakdown.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        farm = get_user_farm(request.user)
        qs = Transaction.objects.filter(farm=farm, is_deleted=False)

        total_income = qs.filter(type='Income').aggregate(t=Sum('amount'))['t'] or Decimal('0')
        total_expenses = qs.filter(type='Expense').aggregate(t=Sum('amount'))['t'] or Decimal('0')

        # Monthly breakdown — last 12 months
        monthly = (
            qs
            .annotate(month=TruncMonth('date'))
            .values('month', 'type')
            .annotate(total=Sum('amount'))
            .order_by('month')
        )

        # Reshape into {month: {income, expense}}
        monthly_map: dict = {}
        for row in monthly:
            key = row['month'].strftime('%Y-%m')
            if key not in monthly_map:
                monthly_map[key] = {'income': Decimal('0'), 'expense': Decimal('0')}
            if row['type'] == 'Income':
                monthly_map[key]['income'] += row['total']
            else:
                monthly_map[key]['expense'] += row['total']

        # Category breakdown
        cat_breakdown = (
            qs
            .values('category', 'type')
            .annotate(total=Sum('amount'))
            .order_by('-total')
        )

        return Response({
            'total_income': total_income,
            'total_expenses': total_expenses,
            'net_profit': total_income - total_expenses,
            'transaction_count': qs.count(),
            'monthly': monthly_map,
            'by_category': list(cat_breakdown),
        })
