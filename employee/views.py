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
    
    # Get sales data for the current salesperson
    user_sales = Sales.objects.filter(user=user, status='Completed')
    
    # Daily sales amount - total sales amount for today
    daily_sales_amount = user_sales.filter(
        sale_date__date=today
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Calculate daily sales growth (compare to yesterday)
    yesterday = today - timedelta(days=1)
    yesterday_sales = user_sales.filter(
        sale_date__date=yesterday
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    daily_growth = 0
    if yesterday_sales > 0:
        daily_growth = ((daily_sales_amount - yesterday_sales) / yesterday_sales) * 100
    elif daily_sales_amount > 0:
        daily_growth = 100
    
    # Monthly sales amount - total sales amount for current month
    current_month = today.month
    current_year = today.year
    monthly_sales_amount = user_sales.filter(
        sale_date__month=current_month,
        sale_date__year=current_year
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Weekly sales amount - total sales amount for the last 7 days
    week_ago = today - timedelta(days=7)
    weekly_sales_amount = user_sales.filter(
        sale_date__date__gte=week_ago
    ).aggregate(total=Sum('total_amount'))['total'] or 0
    
    # Total number of sales
    total_sales_count = user_sales.count()
    
    # Recent transactions (last 5 sales)
    recent_transactions = Sales.objects.filter(
        user=user
    ).select_related('customer').prefetch_related(
        'items__product'
    ).order_by('-sale_date')[:5]
    
    context = {
        'isSalesPerson': True,
        'user': user,
        'daily_sales_amount': daily_sales_amount,
        'daily_growth': daily_growth,
        'monthly_sales_amount': monthly_sales_amount,
        'weekly_sales_amount': weekly_sales_amount,
        'total_sales_count': total_sales_count,
        'recent_transactions': recent_transactions,
    }
    
    return render(request, 'screens/employee/employee-dashboard.html', context)

# Handle invalid employee URLs
def handle_invalid_employee_url(request, invalid_path):
    from django.contrib import messages
    from django.shortcuts import redirect
    
    # Add specific error message with the invalid path
    messages.warning(request, f"The employee page '/employee/{invalid_path}/' was not found. You've been redirected to your dashboard.")
    
    # Redirect to employee dashboard
    return redirect('employee-dashboard')
