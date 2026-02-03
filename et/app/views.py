from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .models import Expense
from django.db.models import Sum

@login_required
def dashboard(request):
    expenses = Expense.objects.filter(user=request.user)
    total = expenses.aggregate(Sum('amount'))['amount__sum'] or 0

    return render(request, 'dashboard.html', {
        'expenses': expenses,
        'total': total
    })
