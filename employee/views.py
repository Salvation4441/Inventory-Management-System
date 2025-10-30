from django.shortcuts import render
from authentication.decorators import allowed_users
from administrator.models import Sales, SalesItem, Product, Customer
from django.db.models import Sum, Count, F
from datetime import datetime, timedelta

# Create your views here.
@allowed_users(allowed_roles=['SALESPERSON'])
def employee_dashboard(request):
    user = request.user
    today = datetime.now().date()
    week_ago = today - timedelta(days=7)
    
    # Get sales data for the current salesperson
    user_sales = Sales.objects.filter(user=user, status='Completed')
    
    # Weekly earnings - total sales amount for the last 7 days
    weekly_earnings = user_sales.filter(
        sale_date__date__gte=week_ago
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Calculate weekly earnings growth (compare to previous week)
    previous_week_start = week_ago - timedelta(days=7)
    previous_week_earnings = user_sales.filter(
        sale_date__date__gte=previous_week_start,
        sale_date__date__lt=week_ago
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    weekly_growth = 0
    if previous_week_earnings > 0:
        weekly_growth = ((weekly_earnings - previous_week_earnings) / previous_week_earnings) * 100
    elif weekly_earnings > 0:
        weekly_growth = 100
    
    # Total number of sales
    total_sales_count = user_sales.count()
    
    # Total sales this month
    current_month = today.month
    current_year = today.year
    monthly_sales_count = user_sales.filter(
        sale_date__month=current_month,
        sale_date__year=current_year
    ).count()
    
    # Recent transactions (last 5 sales)
    recent_transactions = Sales.objects.filter(
        user=user
    ).select_related('customer').prefetch_related(
        'items__product'
    ).order_by('-sale_date')[:5]
    
    context = {
        'isSalesPerson': True,
        'user': user,
        'weekly_earnings': weekly_earnings,
        'weekly_growth': weekly_growth,
        'total_sales_count': total_sales_count,
        'monthly_sales_count': monthly_sales_count,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'screens/employee/employee-dashboard.html', context)
