from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Category(models.Model):
    name = models.CharField(max_length=100)
    
    class Meta:
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name

class Expense(models.Model):

    TRANSACTION_TYPES = [
        ('expense', 'Expense'),
        ('income', 'Income'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField()
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)
    description = models.TextField(blank=True)

    type = models.CharField(
        max_length=10,
        choices=TRANSACTION_TYPES,
        default='expense'
    )

    class Meta:
        indexes = [
            models.Index(fields=['user', '-date']),
        ]
        ordering = ['-date']

class MonthlyBudget(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        unique_together = ('user', 'year', 'month')

    def __str__(self):
        return f"{self.user.username} - {self.month}/{self.year}"