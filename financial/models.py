from django.db import models
from django.conf import settings
from base.models import BaseModel
from account.models import Farm


class Transaction(BaseModel):
    TYPE_CHOICES = [
        ('Income', 'Income'),
        ('Expense', 'Expense'),
    ]

    INCOME_CATEGORIES = [
        ('Livestock Sale', 'Livestock Sale'),
        ('Milk/Dairy', 'Milk/Dairy'),
        ('Egg Sales', 'Egg Sales'),
        ('Wool/Fiber', 'Wool/Fiber'),
        ('Breeding Fee', 'Breeding Fee'),
        ('Grants/Subsidies', 'Grants/Subsidies'),
        ('Other Income', 'Other Income'),
    ]

    EXPENSE_CATEGORIES = [
        ('Feed & Nutrition', 'Feed & Nutrition'),
        ('Veterinary', 'Veterinary'),
        ('Medications', 'Medications'),
        ('Equipment', 'Equipment'),
        ('Labor', 'Labor'),
        ('Utilities', 'Utilities'),
        ('Transportation', 'Transportation'),
        ('Maintenance', 'Maintenance'),
        ('Livestock Purchase', 'Livestock Purchase'),
        ('Other Expense', 'Other Expense'),
    ]

    ALL_CATEGORIES = INCOME_CATEGORIES + EXPENSE_CATEGORIES

    farm = models.ForeignKey(Farm, on_delete=models.CASCADE, related_name='transactions')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)
    category = models.CharField(max_length=50, choices=ALL_CATEGORIES)
    description = models.CharField(max_length=255)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    date = models.DateField()
    notes = models.TextField(blank=True, default='')

    class Meta:
        ordering = ['-date', '-created_at']

    def __str__(self):
        return f"{self.type} — {self.description} — ${self.amount}"
